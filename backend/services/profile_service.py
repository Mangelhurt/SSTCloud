"""
profile_service.py — Business logic for profile management.
"""
from typing import Optional, Tuple
from models.user import User
from database import db
from utils.file_handler import save_avatar, delete_avatar


# --------------------------------------------------
# Get profile
# --------------------------------------------------
def get_profile(user_id: int) -> Tuple[Optional[dict], Optional[str]]:
    user = User.query.get(user_id)

    if not user:
        return None, "Usuario no encontrado"

    return user.to_public_dict(), None


# --------------------------------------------------
# Update profile
# --------------------------------------------------
def update_profile(user_id: int, data: dict) -> Tuple[Optional[dict], Optional[str]]:
    """Update basic profile fields."""
    user = User.query.get(user_id)

    if not user:
        return None, "Usuario no encontrado"

    allowed_fields = {"name", "bio", "phone", "location"}

    for field in allowed_fields:
        if field in data:
            value = str(data[field]).strip()

            if field == "name" and not value:
                return None, "El nombre no puede estar vacío"

            setattr(user, field, value)

    db.session.commit()

    return user.to_public_dict(), None


# --------------------------------------------------
# Upload avatar
# --------------------------------------------------
def upload_avatar(user_id: int, file) -> Tuple[Optional[dict], Optional[str]]:
    user = User.query.get(user_id)

    if not user:
        return None, "Usuario no encontrado"

    # Delete old avatar
    if user.avatar:
        delete_avatar(user.avatar)

    filename, error = save_avatar(file, user_id)

    if error:
        return None, error

    user.avatar = filename
    db.session.commit()

    return user.to_public_dict(), None


# --------------------------------------------------
# Remove avatar
# --------------------------------------------------
def remove_avatar(user_id: int) -> Tuple[Optional[dict], Optional[str]]:
    user = User.query.get(user_id)

    if not user:
        return None, "Usuario no encontrado"

    if user.avatar:
        delete_avatar(user.avatar)
        user.avatar = None
        db.session.commit()

    return user.to_public_dict(), None
