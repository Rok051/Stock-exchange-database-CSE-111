import hashlib
import secrets
from functools import wraps
from flask import request, jsonify

# Simple session storage (in-memory for demo)
active_sessions = {}

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token():
    """Generate a secure random session token"""
    return secrets.token_hex(32)

def create_session(user_id, email, full_name, role):
    """Create a new session for a user"""
    token = generate_session_token()
    active_sessions[token] = {
        'user_id': user_id,
        'email': email,
        'full_name': full_name,
        'role': role
    }
    return token

def get_session(token):
    """Get session data from token"""
    return active_sessions.get(token)

def delete_session(token):
    """Remove a session"""
    if token in active_sessions:
        del active_sessions[token]

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        session_token = token.replace('Bearer ', '')
        session = get_session(session_token)
        
        if not session:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        # Add session data to request
        request.current_user = session
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'Authentication required'}), 401
        
        session_token = token.replace('Bearer ', '')
        session = get_session(session_token)
        
        if not session:
            return jsonify({'error': 'Invalid or expired session'}), 401
        
        if session.get('role') != 'ADMIN':
            return jsonify({'error': 'Admin access required'}), 403
        
        request.current_user = session
        return f(*args, **kwargs)
    
    return decorated_function
