"""
auth_service.py — Business logic for authentication.
"""
from typing import Optional, Tuple
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from models.user import User, user_repo

bcrypt = Bcrypt()


def register_demo_user():
    """Seed a demo user so the app works out of the box."""
    if not user_repo.get_by_email("demo@example.com"):
        hashed = bcrypt.generate_password_hash("demo1234").decode("utf-8")
        user_repo.add(User(
            id=0, email="demo@example.com", password_hash=hashed,
            name="Usuario Demo", bio="Hola, soy el usuario de demostración.",
            phone="+57 300 000 0000", location="Bogotá, Colombia",
        ))


def login(email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    """Returns (jwt_token, None) on success or (None, error_message) on failure."""
    user = user_repo.get_by_email(email)
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return None, "Correo o contraseña incorrectos"
    token = create_access_token(identity=str(user.id))
    return token, None


def change_password(user_id: int, current_pwd: str, new_pwd: str) -> Optional[str]:
    """Returns None on success, error string on failure."""
    user = user_repo.get_by_id(user_id)
    if not user:
        return "Usuario no encontrado"
    if not bcrypt.check_password_hash(user.password_hash, current_pwd):
        return "La contraseña actual es incorrecta"
    if len(new_pwd) < 8:
        return "La nueva contraseña debe tener al menos 8 caracteres"
    user.password_hash = bcrypt.generate_password_hash(new_pwd).decode("utf-8")
    user_repo.update(user)
    return None
