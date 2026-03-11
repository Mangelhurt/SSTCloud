"""
models/company.py — Company model for SG-SST platform.

Resolution 0312 / 2019 (MinTrabajo) classification rules:
  - Group  7 → ≤10 workers  AND risk level I, II, or III
  - Group 21 → 11–50 workers AND risk level I, II, or III
  - Group 60 → >50 workers (any risk) OR ≤50 workers with risk IV or V
"""
from datetime import datetime
from database import db

VALID_RISK_LEVELS = ("I", "II", "III", "IV", "V")
VALID_GROUPS = (7, 21, 60)


def compute_required_standards(workers_count: int, risk_level: str) -> int:
    """
    Single source of truth for Resolution 0312 classification.
    Pure function — no DB access, no side effects.
    """
    if workers_count < 1:
        raise ValueError("workers_count must be at least 1")
    if risk_level not in VALID_RISK_LEVELS:
        raise ValueError(f"risk_level must be one of {VALID_RISK_LEVELS}")

    if risk_level in ("IV", "V") or workers_count > 50:
        return 60
    if workers_count >= 11:
        return 21
    return 7


class Company(db.Model):
    __tablename__ = "companies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    nit = db.Column(db.String(20), unique=True, nullable=False)
    workers_count = db.Column(db.Integer, nullable=False)
    risk_level = db.Column(db.String(3), nullable=False)
    required_standard_count = db.Column(db.Integer, nullable=False, default=7)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relación restaurada — Evidence ya existe
    evidences = db.relationship(
        "Evidence",
        backref="company",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def recalculate_standards(self) -> None:
        self.required_standard_count = compute_required_standards(
            self.workers_count, self.risk_level
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "nit": self.nit,
            "workers_count": self.workers_count,
            "risk_level": self.risk_level,
            "required_standard_count": self.required_standard_count,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def to_public_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "nit": self.nit,
            "workers_count": self.workers_count,
            "risk_level": self.risk_level,
            "required_standard_count": self.required_standard_count,
        }

    def __repr__(self) -> str:
        return (
            f"<Company id={self.id} nit={self.nit!r} "
            f"workers={self.workers_count} risk={self.risk_level} "
            f"standards={self.required_standard_count}>"
        )
