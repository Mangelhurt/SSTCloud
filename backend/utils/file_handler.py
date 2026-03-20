"""
utils/file_handler.py — Manejo de archivos para SSTcloud.

Soporta dos tipos de archivos:
  1. Avatares    → PNG, JPG, WEBP  (redimensiona con Pillow)
  2. Evidencias  → PDF, DOCX, XLSX (guarda directamente, sin procesamiento)

Namespacing en disco:
  uploads/avatars/                        → fotos de perfil
  uploads/evidence/<company_id>/          → documentos de evidencia SG-SST
"""
import os
import uuid
from typing import Optional, Tuple
from PIL import Image
from flask import current_app

# ── Tipos permitidos por categoría ───────────────────────────────────────────
AVATAR_EXTENSIONS    = {"png", "jpg", "jpeg", "webp"}
EVIDENCE_EXTENSIONS  = {"pdf", "docx", "xlsx"}
ALL_EXTENSIONS       = AVATAR_EXTENSIONS | EVIDENCE_EXTENSIONS

MAX_AVATAR_SIZE = (400, 400)
MAX_EVIDENCE_BYTES = 10 * 1024 * 1024  # 10 MB para documentos


def _ext(filename: str) -> str:
    """Retorna la extensión en minúsculas, sin el punto."""
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()


# ── Avatares ──────────────────────────────────────────────────────────────────

def save_avatar(file, user_id: int) -> Tuple[Optional[str], Optional[str]]:
    """
    Valida, redimensiona y guarda una imagen de avatar.
    Retorna (filename, None) en éxito o (None, error) en fallo.
    """
    if not file or not file.filename:
        return None, "No se proporcionó ningún archivo"

    ext = _ext(file.filename)
    if ext not in AVATAR_EXTENSIONS:
        return None, "Formato no permitido. Usa PNG, JPG o WEBP"

    try:
        img = Image.open(file.stream)
        img.thumbnail(MAX_AVATAR_SIZE, Image.LANCZOS)

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        filename = f"avatar_{user_id}_{uuid.uuid4().hex}.jpg"
        folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "avatars")
        os.makedirs(folder, exist_ok=True)
        img.save(os.path.join(folder, filename), "JPEG", quality=85)
        return filename, None

    except Exception as exc:
        return None, f"Error al procesar la imagen: {str(exc)}"


def delete_avatar(filename: str) -> None:
    """Elimina un avatar del disco. Silencioso si no existe."""
    try:
        folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "avatars")
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


# ── Evidencias ────────────────────────────────────────────────────────────────

def save_evidence(file, company_id: int, standard_id: int) -> Tuple[Optional[str], Optional[str]]:
    """
    Valida y guarda un archivo de evidencia SG-SST.

    - Solo acepta PDF, DOCX, XLSX.
    - Máximo 10 MB.
    - Guarda en uploads/evidence/<company_id>/
    - El filename en disco es generado internamente (UUID).
    - El nombre original se preserva en la BD (original_name), nunca en disco.

    Retorna (filename, None) en éxito o (None, error) en fallo.
    """
    if not file or not file.filename:
        return None, "No se proporcionó ningún archivo"

    ext = _ext(file.filename)
    if ext not in EVIDENCE_EXTENSIONS:
        return None, "Formato no permitido. Usa PDF, DOCX o XLSX"

    # Verificar tamaño leyendo el stream
    file.stream.seek(0, 2)          # ir al final
    size = file.stream.tell()       # posición = tamaño en bytes
    file.stream.seek(0)             # volver al inicio para guardar

    if size > MAX_EVIDENCE_BYTES:
        mb = size / (1024 * 1024)
        return None, f"El archivo supera el límite de 10 MB ({mb:.1f} MB)"

    if size == 0:
        return None, "El archivo está vacío"

    try:
        filename = f"evidence_{company_id}_{standard_id}_{uuid.uuid4().hex}.{ext}"
        folder = os.path.join(
            current_app.config["UPLOAD_FOLDER"], "evidence", str(company_id)
        )
        os.makedirs(folder, exist_ok=True)
        file.save(os.path.join(folder, filename))
        return filename, None

    except Exception as exc:
        return None, f"Error al guardar el archivo: {str(exc)}"


def delete_evidence(filename: str, company_id: int) -> None:
    """Elimina un archivo de evidencia del disco. Silencioso si no existe."""
    try:
        folder = os.path.join(
            current_app.config["UPLOAD_FOLDER"], "evidence", str(company_id)
        )
        path = os.path.join(folder, filename)
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass
