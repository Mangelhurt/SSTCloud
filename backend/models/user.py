from database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    name = db.Column(db.String(120), nullable=False)

    bio = db.Column(db.Text, default="")
    phone = db.Column(db.String(50), default="")
    location = db.Column(db.String(120), default="")

    avatar = db.Column(db.String(255), nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────────
    # uselist=False  → enforces 1:1 at the ORM level (one company per user).
    # lazy="select"  → NOT loaded unless explicitly accessed; zero impact on
    #                   existing auth/profile queries that never touch .company.
    company = db.relationship(
        "Company",
        backref="owner",
        uselist=False,
        lazy="select",
    )

    # -------------------------------------

    def to_public_dict(self):
        """Safe data returned to frontend."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "bio": self.bio,
            "phone": self.phone,
            "location": self.location,
            "avatar": self.avatar,
        }
