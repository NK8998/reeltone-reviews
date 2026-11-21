from .. import film_bp
from ...auth.oidc import viewer_id
from flask import request, jsonify
from api.util.db_helper import get_db_connection, lock_interaction
from datetime import datetime


def like_film(user_id, film_id):
    """Adds a like to a review by a specific user."""

    with get_db_connection() as conn:
        lock_interaction(conn, 'film-like', user_id, film_id)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM film_likes WHERE user_id = %s AND film_id = %s", (user_id, film_id))
        existing = cursor.fetchone()

        if existing:
            # User already liked — remove the like
            cursor.execute("DELETE FROM film_likes WHERE user_id = %s AND film_id = %s", (user_id, film_id))
            return {"message": "Like removed."}
        else:
            # User hasn't liked yet — insert new like
            cursor.execute("""
                INSERT INTO film_likes (user_id, film_id)
                VALUES (%s, %s)
            """, (user_id, film_id))
            return {"message": "Film liked."}


@film_bp.route('/like', methods=['POST'])
def like_film_route():
    """Endpoint to like a film."""
    try:
        data = request.get_json()
        user_id = viewer_id()
        film_id = data.get("film_id")

        if not all([user_id, film_id]):
            return jsonify({"error": "Missing user_id or film_id."}), 400

        message = like_film(user_id, film_id)
    
        return jsonify({"message": message}), 201

    except Exception as e:
        print(f"Error liking review: {e}")
        return jsonify({"error": "Failed to like film.", "details": str(e)}), 500
