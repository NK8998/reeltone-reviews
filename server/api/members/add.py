import sqlite3
from contextlib import closing
from pathlib import Path


def add_member(user_id, username, email, pfp_url):
    path = Path(__file__).resolve().parents[2] / 'db' / 'reeltone.db'
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute('BEGIN IMMEDIATE')
        updated = connection.execute(
            'UPDATE members SET username = ?, email = ?, pfp_url = ? WHERE user_id = ?',
            (username, email, pfp_url, user_id),
        )
        if not updated.rowcount:
            connection.execute(
                'INSERT INTO members (user_id, username, email, pfp_url) VALUES (?, ?, ?, ?)',
                (user_id, username, email, pfp_url),
            )
