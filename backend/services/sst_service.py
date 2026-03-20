"""
services/sst_service.py — Lógica de negocio SG-SST para SSTcloud.

Responsabilidades:
  1. Empresa    → crear, obtener, actualizar
  2. Estándares → listar los aplicables a la empresa del usuario
  3. Evidencias → subir (1 por estándar), eliminar, listar
  4. Cumplimiento → calcular porcentaje y estándares pendientes

Regla de autorización en todas las funciones:
  La empresa se busca siempre filtrando por user_id — nunca solo por company_id.
  Esto evita que un usuario acceda a datos de otra empresa (IDOR).
"""
from typing import Optional, Tuple
from models.company import Company, compute_required_standards, VALID_RISK_LEVELS
from models.standard import Standard
from models.evidence import Evidence
from database import db
from utils.file_handler import save_evidence, delete_evidence


# ── Helpers internos ──────────────────────────────────────────────────────────

def _get_company(user_id: int) -> Optional[Company]:
    """Retorna la empresa del usuario o None si no tiene."""
    return Company.query.filter_by(user_id=user_id).first()


# ═════════════════════════════════════════════════════════════════════════════
# 1. EMPRESA
# ═════════════════════════════════════════════════════════════════════════════

def get_company(user_id: int) -> Tuple[Optional[dict], Optional[str]]:
    """Obtiene la empresa del usuario autenticado."""
    company = _get_company(user_id)
    if not company:
        return None, "La empresa no existe. Registra tu empresa primero."
    return company.to_dict(), None


def create_company(user_id: int, data: dict) -> Tuple[Optional[dict], Optional[str]]:
    """
    Crea la empresa del usuario.
    Un usuario solo puede tener una empresa — retorna error si ya tiene una.
    """
    if _get_company(user_id):
        return None, "Ya tienes una empresa registrada."

    # Validar campos requeridos
    name = str(data.get("name", "")).strip()
    nit  = str(data.get("nit",  "")).strip()
    risk_level = str(data.get("risk_level", "")).strip().upper()

    try:
        workers_count = int(data.get("workers_count", 0))
    except (TypeError, ValueError):
        return None, "El número de trabajadores debe ser un entero válido."

    if not name:
        return None, "El nombre de la empresa es requerido."
    if not nit:
        return None, "El NIT es requerido."
    if workers_count < 1:
        return None, "El número de trabajadores debe ser al menos 1."
    if risk_level not in VALID_RISK_LEVELS:
        return None, f"El nivel de riesgo debe ser uno de: {', '.join(VALID_RISK_LEVELS)}."

    # Verificar NIT único en la plataforma
    if Company.query.filter_by(nit=nit).first():
        return None, f"El NIT {nit} ya está registrado en la plataforma."

    company = Company(
        name=name,
        nit=nit,
        workers_count=workers_count,
        risk_level=risk_level,
        user_id=user_id,
    )
    company.recalculate_standards()

    db.session.add(company)
    db.session.commit()
    return company.to_dict(), None


def update_company(user_id: int, data: dict) -> Tuple[Optional[dict], Optional[str]]:
    """
    Actualiza los datos de la empresa.
    Si cambian workers_count o risk_level, recalcula required_standard_count.
    """
    company = _get_company(user_id)
    if not company:
        return None, "La empresa no existe."

    recalculate = False

    if "name" in data:
        name = str(data["name"]).strip()
        if not name:
            return None, "El nombre no puede estar vacío."
        company.name = name

    if "workers_count" in data:
        try:
            workers_count = int(data["workers_count"])
        except (TypeError, ValueError):
            return None, "El número de trabajadores debe ser un entero válido."
        if workers_count < 1:
            return None, "El número de trabajadores debe ser al menos 1."
        company.workers_count = workers_count
        recalculate = True

    if "risk_level" in data:
        risk_level = str(data["risk_level"]).strip().upper()
        if risk_level not in VALID_RISK_LEVELS:
            return None, f"El nivel de riesgo debe ser uno de: {', '.join(VALID_RISK_LEVELS)}."
        company.risk_level = risk_level
        recalculate = True

    if recalculate:
        company.recalculate_standards()

    db.session.commit()
    return company.to_dict(), None


# ═════════════════════════════════════════════════════════════════════════════
# 2. ESTÁNDARES
# ═════════════════════════════════════════════════════════════════════════════

def get_applicable_standards(user_id: int) -> Tuple[Optional[list], Optional[str]]:
    """
    Lista los estándares que aplican a la empresa del usuario.
    Filtra por group <= empresa.required_standard_count.
    Incluye si el estándar ya tiene evidencia subida.
    """
    company = _get_company(user_id)
    if not company:
        return None, "La empresa no existe."

    standards = (
        Standard.query
        .filter(Standard.group <= company.required_standard_count)
        .order_by(Standard.code)
        .all()
    )

    # Obtener IDs de estándares que ya tienen evidencia para esta empresa
    evidenced_ids = {
        row.standard_id
        for row in Evidence.query
        .filter_by(company_id=company.id)
        .with_entities(Evidence.standard_id)
        .all()
    }

    result = []
    for s in standards:
        item = s.to_dict()
        item["has_evidence"] = s.id in evidenced_ids
        result.append(item)

    return result, None


# ═════════════════════════════════════════════════════════════════════════════
# 3. EVIDENCIAS
# ═════════════════════════════════════════════════════════════════════════════

def upload_evidence(
    user_id: int,
    standard_id: int,
    file,
) -> Tuple[Optional[dict], Optional[str]]:
    """
    Sube un archivo de evidencia para un estándar.
    Regla: solo un archivo por estándar — si ya existe, lo reemplaza.
    """
    company = _get_company(user_id)
    if not company:
        return None, "La empresa no existe."

    # Verificar que el estándar existe y aplica a esta empresa
    standard = Standard.query.filter(
        Standard.id == standard_id,
        Standard.group <= company.required_standard_count,
    ).first()

    if not standard:
        return None, "El estándar no existe o no aplica a tu empresa."

    # Si ya existe evidencia para este estándar, eliminar la anterior
    existing = Evidence.query.filter_by(
        company_id=company.id,
        standard_id=standard_id,
    ).first()

    if existing:
        delete_evidence(existing.filename, company.id)
        db.session.delete(existing)

    # Guardar nuevo archivo
    filename, error = save_evidence(file, company.id, standard_id)
    if error:
        return None, error

    evidence = Evidence(
        filename=filename,
        original_name=file.filename,
        company_id=company.id,
        standard_id=standard_id,
    )
    db.session.add(evidence)
    db.session.commit()
    return evidence.to_dict(), None


def delete_evidence_file(
    user_id: int,
    evidence_id: int,
) -> Tuple[Optional[dict], Optional[str]]:
    """Elimina una evidencia. Verifica que pertenece a la empresa del usuario."""
    company = _get_company(user_id)
    if not company:
        return None, "La empresa no existe."

    evidence = Evidence.query.filter_by(
        id=evidence_id,
        company_id=company.id,
    ).first()

    if not evidence:
        return None, "La evidencia no existe o no pertenece a tu empresa."

    delete_evidence(evidence.filename, company.id)
    db.session.delete(evidence)
    db.session.commit()
    return {"message": "Evidencia eliminada correctamente."}, None


def get_standard_evidence(
    user_id: int,
    standard_id: int,
) -> Tuple[Optional[dict], Optional[str]]:
    """Retorna la evidencia de un estándar específico (o None si no tiene)."""
    company = _get_company(user_id)
    if not company:
        return None, "La empresa no existe."

    evidence = Evidence.query.filter_by(
        company_id=company.id,
        standard_id=standard_id,
    ).first()

    if not evidence:
        return {"evidence": None}, None

    return {"evidence": evidence.to_dict()}, None


# ═════════════════════════════════════════════════════════════════════════════
# 4. CUMPLIMIENTO
# ═════════════════════════════════════════════════════════════════════════════

def get_compliance(user_id: int) -> Tuple[Optional[dict], Optional[str]]:
    """
    Calcula el porcentaje de cumplimiento SG-SST de la empresa.

    Retorna:
      - required:   total de estándares que aplican
      - completed:  estándares que tienen al menos una evidencia
      - pending:    estándares sin evidencia
      - percentage: porcentaje de cumplimiento (0.0 - 100.0)
      - status:     Crítico / Moderado / Aceptable / Excelente
    """
    company = _get_company(user_id)
    if not company:
        return None, "La empresa no existe."

    # Estándares aplicables
    standards = (
        Standard.query
        .filter(Standard.group <= company.required_standard_count)
        .order_by(Standard.code)
        .all()
    )

    # IDs con evidencia
    evidenced_ids = {
        row.standard_id
        for row in Evidence.query
        .filter_by(company_id=company.id)
        .with_entities(Evidence.standard_id)
        .all()
    }

    completed = [s for s in standards if s.id in evidenced_ids]
    pending   = [s for s in standards if s.id not in evidenced_ids]

    required = len(standards)
    n_completed = len(completed)
    percentage = round(n_completed / required * 100, 1) if required > 0 else 0.0

    # Nivel de cumplimiento según rangos del MinTrabajo
    if percentage < 60:
        status = "Crítico"
    elif percentage < 85:
        status = "Moderado"
    elif percentage < 100:
        status = "Aceptable"
    else:
        status = "Excelente"

    return {
        "company": company.to_public_dict(),
        "required": required,
        "completed": n_completed,
        "pending_count": len(pending),
        "percentage": percentage,
        "status": status,
        "pending_standards": [s.to_dict() for s in pending],
        "completed_standards": [s.to_dict() for s in completed],
    }, None
