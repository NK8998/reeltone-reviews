import os
from datetime import datetime
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
import tmdbsimple as tmdb
from werkzeug.middleware.proxy_fix import ProxyFix
from api import api_bp
from api.auth.oidc import init_auth
from api.util.db_helper import get_db_connection
from dotenv import load_dotenv
from psycopg import Error
load_dotenv()

class ReviewsJSONProvider(DefaultJSONProvider):
    @staticmethod
    def default(value):
        if isinstance(value, datetime):
            return value.isoformat()
        return DefaultJSONProvider.default(value)


app = Flask(__name__)
app.json = ReviewsJSONProvider(app)

ENV = os.environ.get("APP_ENV", "development").lower()
app.config['APP_ENV'] = ENV
init_auth(app)
tmdb.API_KEY = os.environ.get("TMDB_API_KEY")
app.config['TMDB_AVAILABLE'] = bool(tmdb.API_KEY)
if not tmdb.API_KEY and ENV != "development":
    raise RuntimeError("TMDB_API_KEY not set in environment")

if ENV == "development":
    CORS(app, resources={r"/*": {"origins": "*"}})
else:
    CORS(app, resources={r"/*": {"origins": [
        "https://reeltone.site",
        "https://www.reeltone.site"
    ]}})

app.register_blueprint(api_bp)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


@app.get('/readyz')
def ready():
    try:
        with get_db_connection() as connection:
            connection.execute('SELECT 1 FROM reviews_sessions LIMIT 1')
        return {'status': 'ready'}
    except Error:
        return {'status': 'unavailable'}, 503


for rule in app.url_map.iter_rules():
    print(f"Route: {rule}")

if __name__ == "__main__":
    port = 5000 if ENV == "development" else 8888
    debug = ENV == "development"
    print(f"Starting app in {ENV} mode on port {port} (debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)
