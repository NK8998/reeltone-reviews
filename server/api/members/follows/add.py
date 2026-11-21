from .. import members_bp
from ...auth.oidc import viewer_id
from flask import request, jsonify
from api.util.db_helper import get_db_connection, lock_interaction

def add_following(follower_id, followed_id):
    """Adds a following relationship between two users."""
    with get_db_connection() as conn:
        lock_interaction(conn, 'follow', follower_id, followed_id)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM followers WHERE follower_id = %s AND followed_id = %s", (follower_id, followed_id))
        existing = cursor.fetchone()
        if not existing:
            cursor.execute("""
                INSERT INTO followers (follower_id, followed_id)
                VALUES (%s, %s)
            """, (follower_id, followed_id))
            return {"message": "Following relationship added."}
        
        else:
            # Remove the following relationship if it already exists
            cursor.execute("DELETE FROM followers WHERE follower_id = %s AND followed_id = %s", (follower_id, followed_id))
            return {"message": "Unfollowed user."}


@members_bp.route('/follows/add', methods=['POST'])
def add_following_route():
    """Endpoint to add a following relationship."""
    try:
        data = request.get_json()
        follower_id = viewer_id()
        followed_id = data.get("followed_id")

        if not follower_id or not followed_id:
            return jsonify({"error": "Missing follower_id or followed_id."}), 400

        add_following(follower_id, followed_id)
        return jsonify({"message": "Following relationship added."}), 201

    except Exception as e:
        print(f"Error adding following relationship: {e}")
        return jsonify({"error": "Failed to add following relationship.", "details": str(e)}), 500