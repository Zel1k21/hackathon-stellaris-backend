import os
from flask import Flask
from dotenv import load_dotenv
from internal.app.handler.handler import register_routes


def run():
    """Run the Flask application"""
    app = Flask(__name__)

    # Register all routes
    register_routes(app)

    # Start the Flask development server
    port = os.getenv("API_PORT")
    print(f"Starting Flask server on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
