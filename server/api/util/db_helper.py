import json
import os

import psycopg


def get_db_connection():
    return psycopg.connect(
        host=os.getenv('PGHOST', '127.0.0.1'),
        port=os.getenv('PGPORT', '5433'),
        dbname=os.getenv('PGDATABASE', 'reeltone_reviews'),
        user=os.getenv('PGUSER', 'reeltone_reviews'),
        connect_timeout=5,
        options='-c timezone=UTC',
    )


def lock_interaction(connection, operation, *subjects):
    key = json.dumps(['reviews', operation, *map(str, subjects)])
    connection.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))', (key,))
