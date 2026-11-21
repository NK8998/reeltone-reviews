from .. import film_bp
from ...auth.oidc import viewer_id
from flask import request, jsonify
from api.util.db_helper import get_db_connection, lock_interaction

def add_to_watched(user_id, film_id, film_title, film_poster):
    """Adds a film to the user's watched list."""

    with get_db_connection() as conn:
        lock_interaction(conn, 'watched', user_id, film_id)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM watched WHERE user_id = %s AND film_id = %s", (user_id, film_id))
        existing = cursor.fetchone()

        if existing:
            # Film already in watched list
            cursor.execute("""DELETE FROM watched WHERE user_id = %s AND film_id = %s""", (user_id, film_id))
            return {"message": "Film removed from watched list."}
        else:
            # Film not in watched list, insert it
            cursor.execute("""
                INSERT INTO watched (user_id, film_id, film_title, film_poster)
                VALUES (%s, %s, %s, %s)
            """, (user_id, film_id, film_title, film_poster))
            return {"message": "Film added to watched list."}

@film_bp.route('/watched', methods=['POST'])
def add_watched_route():
    """Endpoint to add a film to the watched list."""
    try:
        data = request.get_json()
        user_id = viewer_id()
        film_id = data.get("film_id")
        film_title = data.get("film_title")
        film_poster = data.get("film_poster")

        if not all([user_id, film_id, film_title, film_poster]):
            return jsonify({"error": "Missing user_id, film_id, film_title, or film_poster."}), 400
        
        message = add_to_watched(user_id, film_id, film_title, film_poster)
        return jsonify({"message": message}), 201
    except Exception as e:
        print(f"Error adding film to watched list: {e}")
        return jsonify({"error": "Failed to add film to watched list.", "details": str(e)}), 500
