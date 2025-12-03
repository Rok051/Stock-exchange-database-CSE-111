import hashlib
import secrets
from functools import wraps
from flask import request, jsonify

# Simple in-memory session storage (OK for demo / project)
active_sessions = {}


def hash_password(password: str) -> str:
    # Hash the password with SHA-256
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def generate_session_token() -> str:
    # Generate a random session token
    return secrets.token_hex(32)


def create_session(user_id: str, email: str, full_name: str, role: str) -> str:
    # Create a session and return the token
    # Frontend sends this as: Authorization: Bearer <token>
    token = generate_session_token()
    active_sessions[token] = {
        "user_id": user_id,
        "email": email,
        "full_name": full_name,
        "role": role,
    }
    return token


def get_session(token: str):
    # Get the session data, or None if expired
    return active_sessions.get(token)


def delete_session(token: str) -> None:
    # Remove the session when user logs out
    if token in active_sessions:
        del active_sessions[token]


def _get_token_from_header():
    # Pull the token from the Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.replace("Bearer ", "", 1).strip()


def require_auth(f):
    # Decorator that makes sure the user is logged in
    # Loads their session and attaches it to the request

    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = _get_token_from_header()
        if not session_token:
            return jsonify({"error": "Authentication required"}), 401

        session = get_session(session_token)
        if not session:
            return jsonify({"error": "Invalid or expired session"}), 401

        # Attach session to the request so other functions can use it
        request.current_user = session
        return f(*args, **kwargs)

    return decorated_function


def require_admin(f):
    # Same as require_auth but also checks if user is an admin

    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = _get_token_from_header()
        if not session_token:
            return jsonify({"error": "Authentication required"}), 401

        session = get_session(session_token)
        if not session:
            return jsonify({"error": "Invalid or expired session"}), 401

        if session.get("role") != "ADMIN":
            return jsonify({"error": "Admin access required"}), 403

        request.current_user = session
        return f(*args, **kwargs)

    return decorated_function
