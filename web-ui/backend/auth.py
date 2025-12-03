import hashlib
import secrets
from functools import wraps
from flask import request, jsonify

# Simple in-memory session storage (OK for demo / project)
active_sessions = {}


def hash_password(password: str) -> str:
    """Hash a plaintext password using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def generate_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_hex(32)


def create_session(user_id: str, email: str, full_name: str, role: str) -> str:
    """
    Create a new session for a user and return the token.
    The token is what the frontend stores and sends as:
    Authorization: Bearer <token>
    """
    token = generate_session_token()
    active_sessions[token] = {
        "user_id": user_id,
        "email": email,
        "full_name": full_name,
        "role": role,
    }
    return token


def get_session(token: str):
    """Get session data from token, or None if not found."""
    return active_sessions.get(token)


def delete_session(token: str) -> None:
    """Remove a session (used on logout)."""
    if token in active_sessions:
        del active_sessions[token]


def _get_token_from_header():
    """Internal helper: extract bare token from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    return auth_header.replace("Bearer ", "", 1).strip()


def require_auth(f):
    """
    Decorator to require authentication.
    - Looks up the session from the Authorization header
    - Attaches session as request.current_user
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_token = _get_token_from_header()
        if not session_token:
            return jsonify({"error": "Authentication required"}), 401

        session = get_session(session_token)
        if not session:
            return jsonify({"error": "Invalid or expired session"}), 401

        # Attach session data to the request for downstream handlers
        request.current_user = session
        return f(*args, **kwargs)

    return decorated_function


def require_admin(f):
    """
    Decorator to require an authenticated user with ADMIN role.
    """

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
