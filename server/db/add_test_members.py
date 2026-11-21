import sqlite3

DB_PATH = "reeltone.db"

test_members = [
    ("user_001", "john_doe", "john@example.com", "/svgs/default-user-icon.svg"),
    ("user_002", "jane_smith", "jane@example.com", "/svgs/default-user-icon.svg"),
    ("user_003", "movie_buff", "buff@example.com", "/svgs/default-user-icon.svg"),
]

with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    for user_id, username, email, pfp_url in test_members:
        cursor.execute("""
            INSERT INTO members (user_id, username, email, pfp_url)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, email, pfp_url))
    conn.commit()
    print(f"Inserted {len(test_members)} test members into the database.")
