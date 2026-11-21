import os

import pytest
import tmdbsimple as tmdb
from dotenv import load_dotenv

from api.film.essential.essential import get_by_id


load_dotenv()


@pytest.mark.skipif(not os.getenv("TMDB_API_KEY"), reason="TMDB_API_KEY is required for this integration test")
def test_get_film_by_id():
    tmdb.API_KEY = os.environ["TMDB_API_KEY"]
    assert get_by_id(541671).get("id") == 541671
