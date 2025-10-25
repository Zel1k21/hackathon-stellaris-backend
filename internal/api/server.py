from flask import Flask
from internal.api.database import get_db_connection
from internal.app.handler.user import register_user_routes


def get_db():
    """Get database connection for repository use"""
    return get_db_connection()


def run():
    """Run the Flask application"""
    app = Flask(__name__)

    # Register all routes
    register_user_routes(app)

    # Start the Flask development server
    print("Starting Flask server on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    run()
