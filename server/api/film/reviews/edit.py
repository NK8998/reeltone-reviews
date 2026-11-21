from .. import film_bp
from ...auth.oidc import viewer_id
from flask import request, jsonify
from api.util.db_helper import get_db_connection


def edit_review(user_id, review_id, new_content, rating):
    """Edit a review by a specific user."""

    with get_db_connection() as conn:
        updated = conn.execute("""
            UPDATE reviews SET review_text = %s, updated_at = now(), rating = %s
            WHERE user_id = %s AND id = %s RETURNING updated_at
        """, (new_content, rating, user_id, review_id)).fetchone()
        if not updated:
            return {"message": "Review not found or user not authorized.", "film_data": {}}
        data = {
            "id": review_id,
            "user_id": user_id,
            "review_text": new_content,
            "rating": rating,
            "updated_at": updated[0].isoformat(),
        }
        return {"message": "Review updated successfully.", "film_data": data}


@film_bp.route('/reviews/edit', methods=['POST'])
def edit_review_route():
    """Endpoint to edit a review."""
    try:
        data = request.get_json()
        user_id = viewer_id()
        review_id = data.get("review_id")
        new_content = data.get("new_content")
        rating = data.get("rating")

        if not all([user_id, review_id, new_content, rating]):
            return jsonify({"error": "Missing user_id, review_id, new_content, or rating."}), 400

        message = edit_review(user_id, review_id, new_content, rating)

        return jsonify(message), 201

    except Exception as e:
        print(f"Error editing review: {e}")
        return jsonify({"error": "Failed to edit review.", "details": str(e)}), 500
