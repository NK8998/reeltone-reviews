import hashlib
import json
import os
from contextlib import closing, contextmanager
from pathlib import Path
import secrets
import sqlite3
import time
from urllib.parse import urlsplit
from uuid import UUID

from authlib.integrations.base_client import OAuthError
from authlib.integrations.flask_client import OAuth
from authlib.integrations.flask_client.apps import FlaskOAuth2App
from flask import abort, current_app, g, jsonify, redirect, request, session
from requests import RequestException

from . import auth_bp


CALLBACK_PATH = '/api/reeltone/auth/callback'
SESSION_AGE = 60 * 60


class ReelToneOAuth2App(FlaskOAuth2App):
    def load_server_metadata(self):
        metadata = super().load_server_metadata()
        issuer = current_app.config['AUTH_ISSUER']
        if metadata.get('issuer') != issuer:
            raise OAuthError('invalid_issuer')

        internal = current_app.config['AUTH_INTERNAL_URL']
        # Discovery can advertise the address it was called on. Use the requested audience
        # for each endpoint while keeping the issuer used for token validation unchanged.
        endpoints = metadata.copy()
        for name, destination in (
            ('authorization_endpoint', issuer),
            ('token_endpoint', internal),
            ('jwks_uri', internal),
            ('userinfo_endpoint', internal),
        ):
            url = urlsplit(metadata.get(name, ''))
            if f'{url.scheme}://{url.netloc}' not in {issuer, internal}:
                raise OAuthError('invalid_issuer_endpoint')
            endpoints[name] = destination + url.path
            if url.query:
                endpoints[name] += '?' + url.query
        return endpoints


def origin(value):
    url = urlsplit(value)
    if url.scheme not in ('http', 'https') or not url.netloc or url.username or url.password:
        raise ValueError('Expected an HTTP(S) origin')
    if url.path not in ('', '/') or url.query or url.fragment:
        raise ValueError('Expected an origin without a path or query')
    return f'{url.scheme}://{url.netloc}'


def init_auth(app):
    issuer = origin(os.getenv('AUTH_ISSUER', 'http://localhost:3000'))
    internal_issuer = origin(os.getenv('AUTH_INTERNAL_URL') or issuer)
    reviews = origin(os.getenv('REVIEWS_ORIGIN', 'http://localhost:3101'))
    secret = os.getenv('REVIEWS_SESSION_SECRET')
    client_id = os.getenv('AUTH_CLIENT_ID', 'reviews-local')
    client_secret = os.getenv('AUTH_CLIENT_SECRET')
    if secret and len(secret) < 32:
        raise ValueError('REVIEWS_SESSION_SECRET must contain at least 32 characters')
    if app.config['APP_ENV'] == 'production' and not all(
        url.startswith('https://') for url in (issuer, internal_issuer, reviews)
    ):
        raise ValueError('Production Reviews and Auth must use HTTPS origins')
    app.config.update(
        SECRET_KEY=secret,
        SESSION_COOKIE_NAME='reeltone_reviews',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=reviews.startswith('https://'),
        SESSION_COOKIE_SAMESITE='Lax',
        REVIEWS_ORIGIN=reviews,
        AUTH_ISSUER=issuer,
        AUTH_INTERNAL_URL=internal_issuer,
        REVIEWS_SESSION_DB=os.getenv('REVIEWS_SESSION_DB') or str(
            Path(app.root_path) / 'db' / 'reviews-sessions.sqlite3'
        ),
        REVIEWS_ADMIN_IDS=frozenset(os.getenv('REVIEWS_ADMIN_IDS', '').split()),
    )
    oauth = OAuth(app)
    app.extensions['reviews_oauth'] = oauth
    if secret and client_secret:
        oauth.register(
            name='reeltone',
            client_cls=ReelToneOAuth2App,
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=f'{internal_issuer}/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid profile email',
                'code_challenge_method': 'S256',
                'token_endpoint_auth_method': 'client_secret_basic',
                'default_timeout': 10,
            },
        )


@contextmanager
def session_db():
    with closing(sqlite3.connect(current_app.config['REVIEWS_SESSION_DB'])) as connection, connection:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS reviews_sessions (
                token_hash TEXT PRIMARY KEY,
                profile TEXT NOT NULL,
                expires_at INTEGER NOT NULL
            )
        ''')
        yield connection


def session_hash():
    token = session.get('review_session')
    return hashlib.sha256(token.encode()).hexdigest() if token else None


def viewer():
    if 'reviews_viewer' not in g:
        g.reviews_viewer = None
        token_hash = session_hash()
        if token_hash:
            with session_db() as db:
                row = db.execute(
                    'SELECT profile FROM reviews_sessions WHERE token_hash = ? AND expires_at > ?',
                    (token_hash, int(time.time())),
                ).fetchone()
            if row:
                g.reviews_viewer = json.loads(row[0])
    return g.reviews_viewer


def viewer_id():
    user = viewer()
    return user['id'] if user else None


def require_viewer():
    user = viewer()
    if not user:
        abort(401)
    return user


def safe_next(value):
    if not value or not value.startswith('/') or value.startswith('//') or '\\' in value:
        return '/me'
    if any(ord(char) < 32 or ord(char) == 127 for char in value):
        return '/me'
    return value


def client():
    configured = current_app.extensions['reviews_oauth'].create_client('reeltone')
    if not configured:
        abort(503, description='Reviews sign-in is not configured.')
    return configured


@auth_bp.get('/login')
def login():
    provider = client()
    state = secrets.token_urlsafe(32)
    now = int(time.time())
    pending = session.get('reviews_attempts', {})
    pending = {key: value for key, value in pending.items() if value[1] > now}
    while len(pending) >= 3:
        pending.pop(next(iter(pending)))
    destination = request.args.get('next')
    if not destination and not current_app.config['TMDB_AVAILABLE']:
        destination = '/members'
    pending[state] = [safe_next(destination), now + 600]
    session['reviews_attempts'] = pending
    params = {'state': state}
    if request.args.get('mode') == 'signup':
        params['login_hint'] = 'signup'
    try:
        return provider.authorize_redirect(current_app.config['REVIEWS_ORIGIN'] + CALLBACK_PATH, **params)
    except (OAuthError, RequestException):
        current_app.logger.warning('ReelTone Auth authorization could not start')
        abort(502, description='ReelTone Auth is temporarily unavailable.')


@auth_bp.get('/callback')
def callback():
    provider = client()
    state = request.args.get('state')
    pending = session.get('reviews_attempts', {})
    attempt = pending.pop(state, None)
    session['reviews_attempts'] = pending
    if not attempt or attempt[1] <= int(time.time()):
        abort(400, description='Sign-in expired. Start again from Reviews.')
    try:
        token = provider.authorize_access_token()
        identity = token.get('userinfo')
        if not identity or not token.get('access_token'):
            abort(400, description='Auth returned an incomplete identity.')
        claims = provider.userinfo(token=token)
        if claims.get('sub') != identity.get('sub'):
            abort(400, description='Auth identity could not be verified.')
        subject = str(UUID(claims['sub']))
    except (OAuthError, RequestException, KeyError, ValueError, TypeError):
        abort(400, description='Sign-in could not finish. Start again from Reviews.')

    if claims.get('email_verified') is not True or not claims.get('email') or not claims.get('preferred_username'):
        abort(400, description='A verified ReelTone account is required.')
    profile = {
        'id': subject,
        'username': claims['preferred_username'],
        'firstName': claims.get('given_name'),
        'lastName': claims.get('family_name'),
        'imageUrl': claims.get('picture'),
    }
    from ..members.add import add_member
    add_member(subject, profile['username'], claims['email'], profile['imageUrl'])

    old_session = session_hash()
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    with session_db() as db:
        db.execute('DELETE FROM reviews_sessions WHERE expires_at <= ? OR token_hash = ?', (now, old_session))
        db.execute('INSERT INTO reviews_sessions VALUES (?, ?, ?)',
                   (hashlib.sha256(token.encode()).hexdigest(), json.dumps(profile), now + SESSION_AGE))
    session.clear()
    session['review_session'] = token
    return redirect(safe_next(attempt[0]), code=303)


@auth_bp.get('/session')
def read_session():
    return jsonify({'user': viewer()})


@auth_bp.post('/logout')
def logout():
    token_hash = session_hash()
    if token_hash:
        with session_db() as db:
            db.execute('DELETE FROM reviews_sessions WHERE token_hash = ?', (token_hash,))
    if current_app.secret_key:
        session.clear()
    return '', 204


@auth_bp.get('/account')
def account():
    require_viewer()
    return redirect(current_app.config['AUTH_ISSUER'] + '/account')


@auth_bp.get('/forgot-password')
def reset_password():
    return redirect(current_app.config['AUTH_ISSUER'] + '/forgot-password')
