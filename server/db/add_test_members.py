from dotenv import load_dotenv

from api.members.add import add_member


if __name__ == '__main__':
    load_dotenv()
    for user_id, username, email in (
        ('user_001', 'john_doe', 'john@example.com'),
        ('user_002', 'jane_smith', 'jane@example.com'),
        ('user_003', 'movie_buff', 'buff@example.com'),
    ):
        add_member(user_id, username, email, '/svgs/default-user-icon.svg')
