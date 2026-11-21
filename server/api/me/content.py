from psycopg.rows import dict_row
from ..auth.oidc import viewer_id
from . import me_bp
from flask import jsonify, request
from api.util.db_helper import get_db_connection

def get_user_content(user_id):
    """Get watched, watchlist as separate lists for the specified user"""

    if not user_id:
        raise ValueError("User ID is required")
    
    with get_db_connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)

        # Fetch watched films with rewatching flag
        watched_query = """
            SELECT
                w.film_id,
                w.film_title,
                w.film_poster,
                w.watched_at,
                EXISTS(
                    SELECT 1
                    FROM watchlist wl
                    WHERE wl.user_id = w.user_id
                    AND wl.film_id = w.film_id
                ) AS rewatching
            FROM watched w
            WHERE w.user_id = %s
            ORDER BY w.watched_at DESC
        """
        cursor.execute(watched_query, (user_id,))
        watched = [dict(row) for row in cursor.fetchall()]

        # Fetch watchlist films with rewatching flag
        watchlist_query = """
            SELECT
                wl.film_id,
                wl.film_title,
                wl.film_poster,
                wl.added_at,
                EXISTS(
                    SELECT 1
                    FROM watched w
                    WHERE w.user_id = wl.user_id
                    AND w.film_id = wl.film_id
                ) AS rewatching
            FROM watchlist wl
            WHERE wl.user_id = %s
            ORDER BY wl.added_at DESC
        """
        cursor.execute(watchlist_query, (user_id,))
        watchlist = [dict(row) for row in cursor.fetchall()]

    return {
        "watched": watched,
        "watchlist": watchlist
    }

    

@me_bp.route("/content", methods=["GET"])
def content():
    try:
        user_id = viewer_id()
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        friends_activity = get_user_content(user_id)
        if not friends_activity:
            return jsonify({"message": "No friends activity found"}), 404
        return jsonify({"friends_activity": friends_activity}), 200
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500