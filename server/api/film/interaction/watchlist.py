from .. import film_bp
from ...auth.oidc import viewer_id
from flask import request, jsonify
from api.util.db_helper import get_db_connection, lock_interaction


def add_to_watchlist(user_id, film_id, film_title, film_poster):
    """Adds a film to the user's watchlist."""

    with get_db_connection() as conn:
        lock_interaction(conn, 'watchlist', user_id, film_id)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM watchlist WHERE user_id = %s AND film_id = %s", (user_id, film_id))
        existing = cursor.fetchone()
        if existing:
            # Film already in watchlist
            cursor.execute("DELETE FROM watchlist WHERE user_id = %s AND film_id = %s", (user_id, film_id))
            return {"message": "Film removed from watchlist.", "is_in_watchlist": False}
        else:
            # Film not in watchlist, insert it
            cursor.execute("""
                INSERT INTO watchlist (user_id, film_id, film_title, film_poster)
                VALUES (%s, %s, %s, %s)
            """, (user_id, film_id, film_title, film_poster))
            return {"message": "Film added to watchlist.", "is_in_watchlist": True}
        
@film_bp.route('/watchlist', methods=['POST'])
def add_watchlist_route():
    """Endpoint to add a film to the watchlist."""
    try:
        data = request.get_json()
        user_id = viewer_id()
        film_id = data.get("film_id")
        film_title = data.get("film_title")
        film_poster = data.get("film_poster")
        if not all([user_id, film_id, film_title, film_poster]):
            return jsonify({"error": "Missing user_id, film_id, film_title, or film_poster."}), 400
        message = add_to_watchlist(user_id, film_id, film_title, film_poster)
        return jsonify({"message": message, }), 201
    except Exception as e:
        print(f"Error adding film to watchlist: {e}")
        return jsonify({"error": "Failed to add film to watchlist.", "details": str(e)}), 500