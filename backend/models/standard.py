"""
models/standard.py — Catálogo de estándares mínimos SG-SST.

Resolución 0312 de 2019 (MinTrabajo).
Filtro de aplicabilidad:
  Standard.query.filter(Standard.group <= empresa.required_standard_count)
"""
from database import db


class Standard(db.Model):
    __tablename__ = "standards"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(300), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    group = db.Column(db.Integer, nullable=False)

    # Relación restaurada — Evidence ya existe
    evidences = db.relationship(
        "Evidence",
        backref="standard",
        lazy="dynamic",
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "category": self.category,
            "group": self.group,
        }

    def __repr__(self) -> str:
        return f"<Standard {self.code!r} group={self.group}>"
