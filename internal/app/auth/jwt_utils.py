import jwt
import datetime
from typing import Optional, Dict, Any
from flask import request, jsonify
from functools import wraps
from internal.app.config import Config


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        days=Config.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, Config.JWT_SECRET_KEY, algorithm=Config.JWT_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(
            token, Config.JWT_SECRET_KEY, algorithms=[Config.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({"error": "Invalid authorization header format"}), 401

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 401

        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        # Check if it's an access token
        if payload.get("type") != "access":
            return jsonify({"error": "Invalid token type"}), 401

        # Add user info to request context
        request.user_id = payload.get("user_id")
        request.user_name = payload.get("user_name")
        request.is_moderator = payload.get("is_moderator", False)

        return f(*args, **kwargs)

    return decorated


def moderator_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not hasattr(request, "is_moderator") or not request.is_moderator:
            return jsonify({"error": "Moderator privileges required"}), 403
        return f(*args, **kwargs)

    return decorated
