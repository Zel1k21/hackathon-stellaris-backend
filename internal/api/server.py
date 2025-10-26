import os
from flask import Flask
from internal.api.database import get_db_connection
from internal.app.handler.user import register_user_routes
from internal.app.handler.observation import register_observation_route


def get_db():
    """Get database connection for repository use"""
    return get_db_connection()


def run():
    """Run the Flask application"""
    app = Flask(__name__)

    # Register all routes
    register_user_routes(app)
    register_observation_route(app)

    # Start the Flask development server
    port = os.getenv("API_PORT")
    print(f"Starting Flask server on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    run()
