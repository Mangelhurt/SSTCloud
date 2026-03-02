"""
User model — In a real project replace the in-memory store
with SQLAlchemy + a proper database (PostgreSQL, MySQL, etc.)
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    id: int
    email: str
    password_hash: str
    name: str
    bio: str = ""
    phone: str = ""
    location: str = ""
    avatar: Optional[str] = None   # filename stored in uploads/

    def to_public_dict(self) -> dict:
        """Return user data safe to send to the client (no password)."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "bio": self.bio,
            "phone": self.phone,
            "location": self.location,
            "avatar": self.avatar,
        }


# ---------------------------------------------------------------------------
# Simple in-memory "database" — swap for SQLAlchemy in production
# ---------------------------------------------------------------------------
class UserRepository:
    def __init__(self):
        self._store: dict = {}
        self._next_id: int = 1

    def add(self, user: "User") -> "User":
        user.id = self._next_id
        self._store[user.id] = user
        self._next_id += 1
        return user

    def get_by_id(self, user_id: int) -> Optional["User"]:
        return self._store.get(user_id)

    def get_by_email(self, email: str) -> Optional["User"]:
        return next((u for u in self._store.values() if u.email == email), None)

    def update(self, user: "User") -> "User":
        self._store[user.id] = user
        return user

    def delete(self, user_id: int) -> bool:
        return bool(self._store.pop(user_id, None))


# Singleton instance shared across the app
user_repo = UserRepository()
