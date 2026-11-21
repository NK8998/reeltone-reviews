from api.util.db_helper import get_db_connection


def add_member(user_id, username, email, pfp_url):
    with get_db_connection() as connection:
        connection.execute(
            '''INSERT INTO members (user_id, username, email, pfp_url) VALUES (%s, %s, %s, %s)
               ON CONFLICT (user_id) DO UPDATE SET username = EXCLUDED.username,
               email = EXCLUDED.email, pfp_url = EXCLUDED.pfp_url''',
            (user_id, username, email, pfp_url),
        )
