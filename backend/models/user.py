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
