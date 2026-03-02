"""
profile_service.py — Business logic for profile management.
"""
from typing import Optional, Tuple
from models.user import user_repo, User
from utils.file_handler import save_avatar, delete_avatar


def get_profile(user_id: int) -> Tuple[Optional[dict], Optional[str]]:
    user = user_repo.get_by_id(user_id)
    if not user:
        return None, "Usuario no encontrado"
    return user.to_public_dict(), None


def update_profile(user_id: int, data: dict) -> Tuple[Optional[dict], Optional[str]]:
    """Update basic profile fields. Only allows whitelisted fields."""
    user = user_repo.get_by_id(user_id)
    if not user:
        return None, "Usuario no encontrado"

    allowed_fields = {"name", "bio", "phone", "location"}
    for field in allowed_fields:
        if field in data:
            value = str(data[field]).strip()
            if field == "name" and not value:
                return None, "El nombre no puede estar vacío"
            setattr(user, field, value)

    user_repo.update(user)
    return user.to_public_dict(), None


def upload_avatar(user_id: int, file) -> Tuple[Optional[dict], Optional[str]]:
    user = user_repo.get_by_id(user_id)
    if not user:
        return None, "Usuario no encontrado"

    # Remove old avatar if exists
    if user.avatar:
        delete_avatar(user.avatar)

    filename, error = save_avatar(file, user_id)
    if error:
        return None, error

    user.avatar = filename
    user_repo.update(user)
    return user.to_public_dict(), None


def remove_avatar(user_id: int) -> Tuple[Optional[dict], Optional[str]]:
    user = user_repo.get_by_id(user_id)
    if not user:
        return None, "Usuario no encontrado"

    if user.avatar:
        delete_avatar(user.avatar)
        user.avatar = None
        user_repo.update(user)

    return user.to_public_dict(), None
