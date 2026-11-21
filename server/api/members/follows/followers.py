from psycopg.rows import dict_row
from api.util.db_helper import get_db_connection
from .. import members_bp
from flask import request, jsonify


def get_followers(user_id):
    """Retrieves full member info for all users who follow the given user_id"""

    with get_db_connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute("""
            SELECT m.id, m.user_id, m.username, m.pfp_url, m.joined_at
            FROM followers f
            JOIN members AS m ON f.follower_id = m.user_id
            WHERE f.followed_id = %s
        """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]



@members_bp.route('/follows/followers', methods=['POST'])
def followers_route():
    """Endpoint to get followers of a user."""
    try:
        data = request.get_json()
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "Missing user_id."}), 400

        followers = get_followers(user_id)
        return jsonify({"followers": followers}), 200

    except Exception as e:
        print(f"Error getting followers: {e}")
        return jsonify({"error": "Failed to get followers.", "details": str(e)}), 500
