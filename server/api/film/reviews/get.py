import psycopg
from psycopg.rows import dict_row
from .. import film_bp
from flask import jsonify, request
from api.util.db_helper import get_db_connection

def get_reviews_by_film_id(film_id):
    """Fetch film reviews by film ID."""

    with get_db_connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)
        query = """
        SELECT id, user_id, username, pfp_url, film_id, film_title, film_poster,
               rating, review_text, is_parent, parent_id, created_at
        FROM reviews
        WHERE film_id = %s
        ORDER BY created_at DESC LIMIT 30
        """
        cursor.execute(query, (film_id,))
        return cursor.fetchall()

@film_bp.route('/reviews/get', methods=['GET'])
def get_reviews():
    """Fetch film reviews by film ID."""
    try:
        film_id = request.args.get('film_id', type=int)
        if not film_id:
            return jsonify({'error': 'film_id is required'}), 400
        reviews = get_reviews_by_film_id(film_id)
        if not reviews:
            return jsonify({'message': 'No reviews found for this film'}), 404
        return jsonify({'reviews': reviews}), 200
    except psycopg.Error as e:
        print(f"Database error: {e}")
        return jsonify({'error': 'An error occurred while fetching reviews'}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': 'An internal server error occurred'}), 500
