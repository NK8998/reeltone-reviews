import argparse
import os
import sqlite3
from contextlib import closing
from pathlib import Path

from dotenv import load_dotenv
from psycopg import sql

from api.util.db_helper import get_db_connection


TABLES = {
    'members': 'id user_id username email pfp_url joined_at',
    'reviews': 'id user_id username pfp_url film_id film_title film_poster rating review_text is_parent parent_id like_count created_at updated_at',
    'review_likes': 'id user_id review_id created_at',
    'film_likes': 'id user_id film_id created_at',
    'watchlist': 'id user_id film_id film_title film_poster added_at',
    'watched': 'id user_id film_id film_title film_poster watched_at',
    'followers': 'id follower_id followed_id followed_at',
}
SESSIONS = {'reviews_sessions': 'token_hash profile expires_at'}
USER_IDS = {'user_id', 'follower_id', 'followed_id'}


def copy_legacy(connection, path, tables, marker):
    if connection.execute('SELECT 1 FROM reviews_migrations WHERE name = %s', (marker,)).fetchone():
        return

    with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as sqlite:
        sqlite.execute('BEGIN')
        sequences = {}
        if sqlite.execute("SELECT 1 FROM sqlite_master WHERE name = 'sqlite_sequence'").fetchone():
            sequences = dict(sqlite.execute('SELECT name, seq FROM sqlite_sequence'))
        for table, names in tables.items():
            columns = names.split()
            target = sql.Identifier(table)
            if connection.execute(sql.SQL('SELECT 1 FROM {} LIMIT 1').format(target)).fetchone():
                raise RuntimeError(f'Cannot import SQLite into populated table {table}')
            legacy_rows = sqlite.execute(f'SELECT {", ".join(columns)} FROM {table}')
            insert = sql.SQL('INSERT INTO {} ({}) VALUES ({})').format(
                target, sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join(sql.Placeholder() for _ in columns),
            )
            count = 0
            highest_id = sequences.get(table, 0)
            with connection.cursor() as cursor:
                for values in legacy_rows:
                    row = tuple(
                        str(value) if value is not None and column in USER_IDS
                        else bool(value) if value is not None and column == 'is_parent'
                        else value
                        for column, value in zip(columns, values)
                    )
                    cursor.execute(insert, row)
                    count += 1
                    if columns[0] == 'id':
                        highest_id = max(highest_id, row[0])
            if highest_id:
                connection.execute(sql.SQL('ALTER TABLE {} ALTER COLUMN id RESTART WITH {}').format(
                    target, sql.Literal(highest_id + 1),
                ))
            print(f'Imported {count} rows into {table}')
    connection.execute('INSERT INTO reviews_migrations (name) VALUES (%s)', (marker,))


def migrate(legacy=None, sessions=None):
    with get_db_connection() as connection:
        connection.execute('SELECT pg_advisory_xact_lock(80410365)')
        connection.execute('CREATE TABLE IF NOT EXISTS reviews_migrations (name text PRIMARY KEY)')
        applied = {row[0] for row in connection.execute('SELECT name FROM reviews_migrations')}
        for migration in sorted(Path(__file__).with_name('db').joinpath('migrations').glob('*.sql')):
            if migration.name in applied:
                continue
            connection.execute(migration.read_text())
            connection.execute('INSERT INTO reviews_migrations (name) VALUES (%s)', (migration.name,))
            print(f'Applied {migration.name}')
        if legacy:
            copy_legacy(connection, legacy, TABLES, 'legacy-sqlite-reviews-v1')
        if sessions:
            copy_legacy(connection, sessions, SESSIONS, 'legacy-sqlite-sessions-v1')


if __name__ == '__main__':
    load_dotenv()
    def legacy_default(name):
        value = os.getenv(name)
        return value if value and Path(value).is_file() else None

    parser = argparse.ArgumentParser(description='Apply Reviews PostgreSQL migrations')
    parser.add_argument('--sqlite', type=Path, default=legacy_default('REVIEWS_LEGACY_SQLITE_FILE'))
    parser.add_argument('--sqlite-sessions', type=Path, default=legacy_default('REVIEWS_LEGACY_SESSIONS_FILE'))
    args = parser.parse_args()
    migrate(args.sqlite, args.sqlite_sessions)
