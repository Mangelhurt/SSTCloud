"""
routes/profile.py -- Profile endpoints.
"""
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from services.profile_service import get_profile, update_profile, upload_avatar, remove_avatar
from utils.decorators import login_required, get_current_user_id

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.route("", methods=["GET"])
@login_required
def handle_get_profile():
    data, error = get_profile(get_current_user_id())
    if error:
        return jsonify({"error": error}), 404
    return jsonify(data), 200


@profile_bp.route("", methods=["PUT"])
@login_required
def handle_update_profile():
    data = request.get_json(silent=True) or {}
    updated, error = update_profile(get_current_user_id(), data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(updated), 200


@profile_bp.route("/avatar", methods=["POST"])
@login_required
def handle_upload_avatar():
    file = request.files.get("avatar")
    if not file:
        return jsonify({"error": "No se encontro el archivo avatar"}), 400
    updated, error = upload_avatar(get_current_user_id(), file)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(updated), 200


@profile_bp.route("/avatar", methods=["DELETE"])
@login_required
def handle_delete_avatar():
    updated, error = remove_avatar(get_current_user_id())
    if error:
        return jsonify({"error": error}), 400
    return jsonify(updated), 200


@profile_bp.route("/avatar/<filename>", methods=["GET"])
def serve_avatar(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
