"""
routes/auth.py — Authentication endpoints.
POST /api/auth/login
POST /api/auth/change-password
"""
from flask import Blueprint, request, jsonify
from services.auth_service import login, change_password
from utils.decorators import login_required, get_current_user_id

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def handle_login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Correo y contraseña son requeridos"}), 400

    token, error = login(email, password)
    if error:
        return jsonify({"error": error}), 401

    return jsonify({"token": token}), 200


@auth_bp.route("/change-password", methods=["POST"])
@login_required
def handle_change_password():
    data = request.get_json(silent=True) or {}
    current_pwd = data.get("current_password", "")
    new_pwd = data.get("new_password", "")

    if not current_pwd or not new_pwd:
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    error = change_password(get_current_user_id(), current_pwd, new_pwd)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Contraseña actualizada correctamente"}), 200
