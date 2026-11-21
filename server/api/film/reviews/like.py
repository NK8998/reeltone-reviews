from .. import film_bp
from ...auth.oidc import viewer_id
from flask import request, jsonify
from api.util.db_helper import get_db_connection, lock_interaction
from datetime import datetime


def like_review(user_id, review_id):
    """Adds a like to a review by a specific user."""

    with get_db_connection() as conn:
        lock_interaction(conn, 'review-like', user_id, review_id)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM review_likes WHERE user_id = %s AND review_id = %s", (user_id, review_id))
        existing = cursor.fetchone()

        if existing:
            # User already liked — remove the like
            cursor.execute("DELETE FROM review_likes WHERE user_id = %s AND review_id = %s", (user_id, review_id))
            return {"message": "Like removed."}
        else:
            # User hasn't liked yet — insert new like
            cursor.execute("""
                INSERT INTO review_likes (user_id, review_id, created_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
            """, (user_id, review_id))
            return {"message": "Review liked."}


@film_bp.route('/reviews/like', methods=['POST'])
def like_review_route():
    """Endpoint to like a review."""
    try:
        data = request.get_json()
        user_id = viewer_id()
        review_id = data.get("review_id")

        if not all([user_id, review_id]):
            return jsonify({"error": "Missing user_id or review_id."}), 400

        message = like_review(user_id, review_id)
    
        return jsonify({"message": message}), 201

    except Exception as e:
        print(f"Error liking review: {e}")
        return jsonify({"error": "Failed to like review.", "details": str(e)}), 500
