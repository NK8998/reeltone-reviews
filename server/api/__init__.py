from flask import Blueprint, current_app, jsonify, request

from .auth import auth_bp
from .auth.oidc import viewer
from .landing import landing_bp
from .me import me_bp
from .films import films_bp
from .film import film_bp
from .members import members_bp
from .search import search_bp

api_bp = Blueprint('api', __name__)

PUBLIC_POSTS = frozenset({
    'api.auth.logout',
    'api.members.discover_members_route',
    'api.members.followers_route',
    'api.members.following_route',
})


@api_bp.before_request
def protect_reviews():
    unsafe = request.method not in ('GET', 'HEAD', 'OPTIONS')
    if unsafe and request.headers.get('Origin') != current_app.config['REVIEWS_ORIGIN']:
        return jsonify(error='Invalid request origin'), 403

    if request.blueprint == 'api.me' or (unsafe and request.endpoint not in PUBLIC_POSTS):
        if not viewer():
            return jsonify(error='Sign in to Reviews'), 401


@api_bp.after_request
def disable_personal_response_caching(response):
    if request.blueprint in {'api.auth', 'api.me', 'api.film', 'api.members'}:
        response.headers['Cache-Control'] = 'private, no-store'
    return response

api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(landing_bp, url_prefix='/landing')
api_bp.register_blueprint(me_bp, url_prefix='/me')
api_bp.register_blueprint(films_bp, url_prefix='/films')
api_bp.register_blueprint(film_bp, url_prefix='/film')
api_bp.register_blueprint(members_bp, url_prefix='/members')
api_bp.register_blueprint(search_bp, url_prefix='/search')
from . import test
