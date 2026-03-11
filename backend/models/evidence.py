"""
models/evidence.py — Archivos de evidencia subidos por las empresas.

Cada registro representa un archivo (PDF, DOCX, XLSX) que una empresa
sube como prueba de cumplimiento de un estándar específico.

Relaciones:
  Evidence → Company  (muchos a uno)
  Evidence → Standard (muchos a uno)

Un estándar se considera CUMPLIDO cuando tiene al menos un Evidence asociado.
"""
from datetime import datetime
from database import db


class Evidence(db.Model):
    __tablename__ = "evidences"

    # ── Primary key ──────────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)

    # ── Archivo ──────────────────────────────────────────────────────────────
    # Nombre del archivo guardado en disco (generado internamente, no el nombre
    # original del usuario). Ejemplo: "evidence_3_12_a1b2c3d4.pdf"
    filename = db.Column(db.String(255), nullable=False)

    # Nombre original del archivo tal como lo subió el usuario.
    # Solo para mostrarlo en la UI — nunca se usa para acceder al disco.
    original_name = db.Column(db.String(255), nullable=False)

    # ── Llaves foráneas ──────────────────────────────────────────────────────
    company_id = db.Column(
        db.Integer,
        db.ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    standard_id = db.Column(
        db.Integer,
        db.ForeignKey("standards.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Auditoría ────────────────────────────────────────────────────────────
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # ── Índice compuesto ─────────────────────────────────────────────────────
    # Acelera la consulta más frecuente: "¿qué estándares tiene evidencia
    # esta empresa?" — usada en cada carga del dashboard de cumplimiento.
    __table_args__ = (
        db.Index("ix_evidence_company_standard", "company_id", "standard_id"),
    )

    # ── Serializer ───────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "filename": self.filename,
            "original_name": self.original_name,
            "company_id": self.company_id,
            "standard_id": self.standard_id,
            "uploaded_at": self.uploaded_at.isoformat(),
        }

    def __repr__(self) -> str:
        return (
            f"<Evidence id={self.id} "
            f"company={self.company_id} standard={self.standard_id} "
            f"file={self.original_name!r}>"
        )
