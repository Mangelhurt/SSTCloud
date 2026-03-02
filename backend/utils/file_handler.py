"""
file_handler.py — Utilities for avatar upload/delete.
"""
import os
import uuid
from typing import Optional, Tuple
from PIL import Image
from flask import current_app

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAX_SIZE = (400, 400)


def _allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_avatar(file, user_id: int) -> Tuple[Optional[str], Optional[str]]:
    """
    Validate, resize, and save an avatar image.
    Returns (filename, None) on success or (None, error) on failure.
    """
    if not file or not file.filename:
        return None, "No se proporcionó ningún archivo"

    if not _allowed(file.filename):
        return None, "Formato no permitido. Usa PNG, JPG o WEBP"

    try:
        img = Image.open(file.stream)
        img.thumbnail(MAX_SIZE, Image.LANCZOS)

        # Convert to RGB to ensure JPEG compatibility
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        ext = "jpg"
        filename = f"avatar_{user_id}_{uuid.uuid4().hex}.{ext}"
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)
        img.save(os.path.join(upload_folder, filename), "JPEG", quality=85)
        return filename, None

    except Exception as exc:
        return None, f"Error al procesar la imagen: {str(exc)}"


def delete_avatar(filename: str) -> None:
    """Silently delete an avatar file."""
    try:
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        path = os.path.join(upload_folder, filename)
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass  # Never raise — deletion failure is non-critical
