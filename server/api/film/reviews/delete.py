from .. import film_bp
from ...auth.oidc import viewer_id
from flask import current_app, request, jsonify
from api.util.db_helper import get_db_connection
from datetime import datetime


def delete_review(user_id, review_id, is_admin=False):
    """Deletes a review by a specific user."""

    if not is_admin:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM reviews WHERE user_id = %s AND id = %s", (user_id, review_id))
            existing = cursor.fetchone()

            if existing:
                cursor.execute("DELETE FROM reviews WHERE user_id = %s AND id = %s", (user_id, review_id))
                return {"message": "Review deleted."}
            else:
                return {"message": "Review not found."}
    else:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM reviews WHERE id = %s", (review_id,))
            existing = cursor.fetchone()
            if not existing:
                return {"message": "Review not found."}
            else:
                cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
                return {"message": "Review deleted by admin."}

@film_bp.route('/reviews/delete', methods=['POST'])
def delete_review_route():
    """Endpoint to delete a review."""
    try:
        data = request.get_json()
        user_id = viewer_id()
        review_id = data.get("review_id")
        is_admin = user_id in current_app.config['REVIEWS_ADMIN_IDS']

        if not all([user_id, review_id]):
            return jsonify({"error": "Missing user_id or review_id."}), 400

        message = delete_review(user_id, review_id, is_admin)

        return jsonify({"message": message}), 201

    except Exception as e:
        print(f"Error deleting review: {e}")
        return jsonify({"error": "Failed to delete review.", "details": str(e)}), 500
