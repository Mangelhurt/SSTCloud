"""
decorators.py — Reusable route decorators.
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def login_required(fn):
    """Protect a route with JWT authentication."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({"error": "Token inválido o expirado. Inicia sesión nuevamente."}), 401
        return fn(*args, **kwargs)
    return wrapper


def get_current_user_id() -> int:
    """Helper to retrieve the user id from the JWT."""
    return int(get_jwt_identity())
