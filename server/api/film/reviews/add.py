from .. import film_bp
from ...auth.oidc import viewer
from flask import request, jsonify
from api.util.db_helper import get_db_connection


def add_review(
        user_id, 
        username, 
        pfp_url, 
        film_id, 
        film_title, 
        film_poster, 
        rating, 
        review_text, 
        is_parent=True, 
        parent_id=None
    ):
    """Insert a film review."""

    try:
        if not all([user_id, film_id, film_title]):
            return {"error": "Missing required fields."}, 400
        

        # Insert the review into the database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reviews (
                    user_id, username, pfp_url,
                    film_id, film_title, film_poster,
                    rating, review_text,
                    is_parent, parent_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, updated_at
            """, (
                user_id, username, pfp_url,
                film_id, film_title, film_poster,
                rating, review_text,
                bool(is_parent), parent_id
            ))
            review_id, updated_at = cursor.fetchone()
            data = {
                "id": review_id,
                "user_id": user_id,
                "username": username,
                "pfp_url": pfp_url,
                "film_id": film_id,
                "film_title": film_title,
                "film_poster": film_poster,
                "rating": rating,
                "review_text": review_text,
                "is_parent": is_parent,
                "parent_id": parent_id,
                "updated_at": updated_at.isoformat()
            }
            return {"message": "Review added successfully.", "film_data": data}
    except Exception as e:
        print(f"Error adding review: {e}")
        return {"error": "Failed to add review."}, 500


@film_bp.route('/reviews/add', methods=['POST'])
def add_review_route():
    """Endpoint to add a new film review."""
    try:
        data = request.get_json()

        user = viewer()
        user_id = user["id"]
        username = user["username"]
        pfp_url = user["imageUrl"]
        film_id = data.get("film_id")
        film_title = data.get("film_title")
        film_poster = data.get("film_poster")
        rating = data.get("rating")
        review_text = data.get("review_text")
        is_parent = data.get("is_parent", True)
        parent_id = data.get("parent_id")

        if not all([user_id, username, film_id, film_title]):
            return jsonify({"error": "Missing required fields."}), 400

        message = add_review(
            user_id=user_id,
            username=username,
            pfp_url=pfp_url,
            film_id=film_id,
            film_title=film_title,
            film_poster=film_poster,
            rating=rating,
            review_text=review_text,
            is_parent=is_parent,
            parent_id=parent_id
        )

        return jsonify(message), 201

    except Exception as e:
        print(f"Error adding review: {e}")
        return jsonify({"error": "Failed to add review.", "details": str(e)}), 500
