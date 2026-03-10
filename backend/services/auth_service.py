"""
auth_service.py — Business logic for authentication.
"""
from typing import Optional, Tuple
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

from models.user import User
from database import db

bcrypt = Bcrypt()


# -------------------------------------------------------------------
# DEMO USER (seed inicial)
# -------------------------------------------------------------------
def register_demo_user():
    """Create demo user if it doesn't exist."""

    user = User.query.filter_by(email="demo@example.com").first()

    if user:
        return

    hashed = bcrypt.generate_password_hash("demo1234").decode("utf-8")

    demo_user = User(
        email="demo@example.com",
        password_hash=hashed,
        name="Usuario Demo",
    )

    db.session.add(demo_user)
    db.session.commit()


# -------------------------------------------------------------------
# LOGIN
# -------------------------------------------------------------------
def login(email: str, password: str) -> Tuple[Optional[str], Optional[str]]:
    """Returns (jwt_token, None) on success or (None, error_message)."""

    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return None, "Correo o contraseña incorrectos"

    token = create_access_token(identity=str(user.id))
    return token, None


# -------------------------------------------------------------------
# CHANGE PASSWORD
# -------------------------------------------------------------------
def change_password(user_id: int, current_pwd: str, new_pwd: str) -> Optional[str]:
    """Returns None on success, error string on failure."""

    user = User.query.get(user_id)

    if not user:
        return "Usuario no encontrado"

    if not bcrypt.check_password_hash(user.password_hash, current_pwd):
        return "La contraseña actual es incorrecta"

    if len(new_pwd) < 8:
        return "La nueva contraseña debe tener al menos 8 caracteres"

    user.password_hash = bcrypt.generate_password_hash(new_pwd).decode("utf-8")

    db.session.commit()

    return None
