from flask import Flask, request, jsonify
from internal.app.repository.user import UserRepository
from internal.models.user import User
from internal.app.auth.jwt_utils import (
    create_access_token,
    create_refresh_token,
    token_required,
)


def register_user_routes(app: Flask):
    @app.route("/users/register", methods=["POST"])
    def create_user():
        try:
            # Get JSON data from request
            data = request.get_json()

            # Validate required fields
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            required_fields = ["name", "password"]
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400

            # Create User object
            user = User(
                id=None,
                name=data["name"],
                password=data["password"],
                is_moderator=data.get("is_moderator", False),
            )

            # Call UserRepository.Create method
            try:
                user_id = UserRepository.Create(user)
            except Exception as db_error:
                return jsonify({"error": f"Database error: {str(db_error)}"}), 500

            # Return success response
            return jsonify(
                {
                    "message": "User created successfully",
                    "user_id": user_id,
                }
            ), 201

        except Exception as e:
            # Handle any unexpected errors
            return jsonify({"error": f"Failed to create user: {str(e)}"}), 500

    @app.route("/users/login", methods=["POST"])
    def login_user():
        try:
            # Get JSON data from request
            data = request.get_json()

            # Validate required fields
            if not data:
                return jsonify({"error": "No JSON data provided"}), 400

            required_fields = ["name", "password"]
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Missing required field: {field}"}), 400

            # Call UserRepository.Authenticate method
            try:
                user_data = UserRepository.Authenticate(data["name"], data["password"])
            except Exception as db_error:
                return jsonify({"error": f"Database error: {str(db_error)}"}), 500

            if not user_data:
                return jsonify({"error": "Invalid username or password"}), 401

            # Create User object from database result
            user = User.from_row(user_data)

            # Create JWT tokens
            token_data = {
                "user_id": user.id,
                "user_name": user.name,
                "is_moderator": user.is_moderator,
            }
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token(token_data)

            # Return success response with tokens
            return jsonify(
                {
                    "message": f"User {user.name} logged in successfully",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "is_moderator": user.is_moderator,
                    },
                }
            ), 200

        except Exception as e:
            # Handle any unexpected errors
            return jsonify({"error": f"Failed to login user: {str(e)}"}), 500

    @app.route("/users/refresh", methods=["POST"])
    def refresh_token():
        try:
            # Get JSON data from request
            data = request.get_json()

            # Validate required fields
            if not data or "refresh_token" not in data:
                return jsonify({"error": "Refresh token is required"}), 400

            refresh_token = data["refresh_token"]

            # Verify refresh token
            from internal.app.auth.jwt_utils import verify_token

            payload = verify_token(refresh_token)

            if not payload or payload.get("type") != "refresh":
                return jsonify({"error": "Invalid or expired refresh token"}), 401

            # Create new access token
            token_data = {
                "user_id": payload.get("user_id"),
                "user_name": payload.get("user_name"),
                "is_moderator": payload.get("is_moderator", False),
            }
            access_token = create_access_token(token_data)

            return jsonify(
                {
                    "access_token": access_token,
                    "user": {
                        "id": token_data["user_id"],
                        "name": token_data["user_name"],
                        "is_moderator": token_data["is_moderator"],
                    },
                }
            ), 200

        except Exception as e:
            return jsonify({"error": f"Failed to refresh token: {str(e)}"}), 500

    @app.route("/users/me", methods=["GET"])
    @token_required
    def get_current_user():
        try:
            return jsonify(
                {
                    "user": {
                        "id": request.user_id,
                        "name": request.user_name,
                        "is_moderator": request.is_moderator,
                    }
                }
            ), 200
        except Exception as e:
            return jsonify({"error": f"Failed to get user info: {str(e)}"}), 500
