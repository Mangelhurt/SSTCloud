"""
routes/sst.py — Endpoints SG-SST para SSTcloud.

Todos los endpoints requieren autenticación JWT (@login_required).

Empresa:
  POST   /api/sst/company        → crear empresa
  GET    /api/sst/company        → obtener empresa
  PUT    /api/sst/company        → actualizar empresa

Estándares:
  GET    /api/sst/standards      → listar estándares aplicables

Evidencias:
  POST   /api/sst/standards/<id>/evidence  → subir evidencia
  GET    /api/sst/standards/<id>/evidence  → obtener evidencia de un estándar
  DELETE /api/sst/evidence/<id>            → eliminar evidencia
  GET    /api/sst/evidence/<filename>      → servir archivo de evidencia

Cumplimiento:
  GET    /api/sst/compliance     → dashboard de cumplimiento
"""
import os
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from utils.decorators import login_required, get_current_user_id
from services.sst_service import (
    get_company,
    create_company,
    update_company,
    get_applicable_standards,
    upload_evidence,
    delete_evidence_file,
    get_standard_evidence,
    get_compliance,
)

sst_bp = Blueprint("sst", __name__, url_prefix="/api/sst")


# ── Empresa ───────────────────────────────────────────────────────────────────

@sst_bp.route("/company", methods=["POST"])
@login_required
def handle_create_company():
    data = request.get_json(silent=True) or {}
    result, error = create_company(get_current_user_id(), data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(result), 201


@sst_bp.route("/company", methods=["GET"])
@login_required
def handle_get_company():
    result, error = get_company(get_current_user_id())
    if error:
        return jsonify({"error": error}), 404
    return jsonify(result), 200


@sst_bp.route("/company", methods=["PUT"])
@login_required
def handle_update_company():
    data = request.get_json(silent=True) or {}
    result, error = update_company(get_current_user_id(), data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(result), 200


# ── Estándares ────────────────────────────────────────────────────────────────

@sst_bp.route("/standards", methods=["GET"])
@login_required
def handle_get_standards():
    result, error = get_applicable_standards(get_current_user_id())
    if error:
        return jsonify({"error": error}), 404
    return jsonify(result), 200


# ── Evidencias ────────────────────────────────────────────────────────────────

@sst_bp.route("/standards/<int:standard_id>/evidence", methods=["POST"])
@login_required
def handle_upload_evidence(standard_id):
    file = request.files.get("evidence")
    if not file:
        return jsonify({"error": "No se encontró el archivo. Usa el campo 'evidence'."}), 400

    result, error = upload_evidence(get_current_user_id(), standard_id, file)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(result), 201


@sst_bp.route("/standards/<int:standard_id>/evidence", methods=["GET"])
@login_required
def handle_get_evidence(standard_id):
    result, error = get_standard_evidence(get_current_user_id(), standard_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(result), 200


@sst_bp.route("/evidence/<int:evidence_id>", methods=["DELETE"])
@login_required
def handle_delete_evidence(evidence_id):
    result, error = delete_evidence_file(get_current_user_id(), evidence_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(result), 200


@sst_bp.route("/evidence/file/<path:filename>", methods=["GET"])
@login_required
def serve_evidence_file(filename):
    """
    Sirve el archivo de evidencia desde disco.
    Requiere autenticación — los documentos no son públicos.
    La ruta incluye el subdirectorio: evidence/<company_id>/<filename>
    """
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    filepath = os.path.join(upload_folder, "evidence", filename)
    directory = os.path.dirname(filepath)
    basename  = os.path.basename(filepath)
    return send_from_directory(directory, basename)


# ── Cumplimiento ──────────────────────────────────────────────────────────────

@sst_bp.route("/compliance", methods=["GET"])
@login_required
def handle_get_compliance():
    result, error = get_compliance(get_current_user_id())
    if error:
        return jsonify({"error": error}), 404
    return jsonify(result), 200
