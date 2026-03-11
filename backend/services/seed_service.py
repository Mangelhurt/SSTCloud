"""
services/seed_service.py — Carga inicial del catálogo SG-SST.

Fuente oficial: Resolución 0312 de 2019, MinTrabajo Colombia.
  Capítulo I   → Artículo 3  → 7 estándares totales
  Capítulo II  → Artículo 9  → 21 estándares totales (7 heredados + 14 nuevos)
  Capítulo III → Artículo 16 → 60 estándares totales (21 heredados + 39 nuevos)

Modelo en BD: 60 registros, clasificados por group = tier donde aparecen por primera vez.
  group=7  → 7 ítems  (aplican a grupos 7, 21, 60)
  group=21 → 14 ítems (aplican a grupos 21 y 60)
  group=60 → 39 ítems (aplican solo al grupo 60)

Filtro de aplicabilidad:
  Standard.query.filter(Standard.group <= empresa.required_standard_count)

IMPORTANTE: Esta función es IDEMPOTENTE.
"""
from models.standard import Standard
from database import db

STANDARDS_CATALOG = [
    # GROUP 7 — 7 ítems
    ("1.1.1","Asignación de persona que diseña e implementa el SG-SST","Planear",7),
    ("1.1.2","Afiliación al Sistema de Seguridad Social Integral","Planear",7),
    ("1.2.1","Plan Anual de Trabajo","Planear",7),
    ("1.3.1","Evaluaciones médicas ocupacionales","Hacer",7),
    ("1.4.1","Identificación de peligros, evaluación y valoración de riesgos","Hacer",7),
    ("1.5.1","Medidas de prevención y control frente a peligros/riesgos identificados","Hacer",7),
    ("1.6.1","Capacitación en SST","Hacer",7),
    # GROUP 21 — 14 ítems nuevos
    ("2.1.1","Asignación de recursos para el SG-SST","Planear",21),
    ("2.2.1","Conformación y funcionamiento del COPASST","Hacer",21),
    ("2.2.2","Conformación y funcionamiento del Comité de Convivencia Laboral","Hacer",21),
    ("2.3.1","Programa de capacitación anual en SST","Hacer",21),
    ("2.4.1","Política de Seguridad y Salud en el Trabajo documentada","Planear",21),
    ("2.5.1","Archivo y retención documental del SG-SST","Planear",21),
    ("2.6.1","Descripción sociodemográfica y diagnóstico de condiciones de salud","Planear",21),
    ("2.6.2","Actividades de medicina del trabajo y de prevención y promoción de salud","Hacer",21),
    ("2.6.3","Restricciones y recomendaciones médico-laborales","Hacer",21),
    ("2.7.1","Reporte de accidentes de trabajo y enfermedades laborales","Hacer",21),
    ("2.7.2","Investigación de incidentes, accidentes de trabajo y enfermedades laborales","Hacer",21),
    ("2.8.1","Mantenimiento periódico de instalaciones, equipos, máquinas y herramientas","Hacer",21),
    ("2.8.2","Entrega de EPP y capacitación en uso adecuado","Hacer",21),
    ("2.9.1","Plan de prevención, preparación y respuesta ante emergencias","Hacer",21),
    # GROUP 60 — 39 ítems nuevos
    ("3.1.1","Asignación de responsabilidades en SST","Planear",60),
    ("3.1.2","Identificación de trabajadores en actividades de alto riesgo y cotización pensión especial","Planear",60),
    ("3.1.3","Capacitación de los integrantes del COPASST","Hacer",60),
    ("3.1.4","Inducción y reinducción en SST","Hacer",60),
    ("3.1.5","Curso virtual de capacitación de 50 horas en SST","Hacer",60),
    ("3.2.1","Objetivos en SST documentados, medibles y cuantificables","Planear",60),
    ("3.2.2","Evaluación inicial del Sistema de Gestión de SST","Planear",60),
    ("3.2.3","Rendición de cuentas","Verificar",60),
    ("3.2.4","Matriz legal actualizada","Planear",60),
    ("3.2.5","Mecanismos de comunicación y auto reporte en SST","Hacer",60),
    ("3.2.6","Identificación y evaluación para adquisición de bienes y servicios","Planear",60),
    ("3.2.7","Evaluación y selección de proveedores y contratistas","Planear",60),
    ("3.2.8","Gestión del cambio","Planear",60),
    ("3.3.1","Perfiles de cargo","Planear",60),
    ("3.3.2","Custodia de las historias clínicas ocupacionales","Hacer",60),
    ("3.3.3","Estilos de vida y entornos saludables","Hacer",60),
    ("3.3.4","Servicios de higiene: baños, agua potable, comedores","Hacer",60),
    ("3.3.5","Manejo de residuos sólidos, líquidos y gaseosos","Hacer",60),
    ("3.4.1","Registro y análisis estadístico de accidentes de trabajo y enfermedades laborales","Verificar",60),
    ("3.5.1","Frecuencia de accidentalidad","Verificar",60),
    ("3.5.2","Severidad de accidentalidad","Verificar",60),
    ("3.5.3","Proporción de accidentes de trabajo mortales","Verificar",60),
    ("3.5.4","Prevalencia de la enfermedad laboral","Verificar",60),
    ("3.5.5","Incidencia de la enfermedad laboral","Verificar",60),
    ("3.5.6","Ausentismo por causa médica","Verificar",60),
    ("3.6.2","Identificación de peligros con participación de todos los niveles de la empresa","Hacer",60),
    ("3.6.3","Identificación de sustancias catalogadas como carcinógenas o con toxicidad aguda","Hacer",60),
    ("3.6.4","Mediciones ambientales, químicas, físicas y biológicas","Verificar",60),
    ("3.7.1","Procedimientos e instructivos internos de SST","Hacer",60),
    ("3.7.2","Inspecciones a instalaciones, maquinaria o equipos","Hacer",60),
    ("3.7.3","Brigada de prevención, preparación y respuesta ante emergencias","Hacer",60),
    ("3.8.1","Definición de indicadores del SG-SST","Verificar",60),
    ("3.8.2","Auditoría anual del SG-SST","Verificar",60),
    ("3.8.3","Revisión por la Alta Dirección","Verificar",60),
    ("3.8.4","Planificación de la auditoría con el COPASST","Verificar",60),
    ("3.9.1","Acciones preventivas y correctivas","Actuar",60),
    ("3.9.2","Acciones de mejora conforme a revisión de la Alta Dirección","Actuar",60),
    ("3.9.3","Acciones de mejora con base en investigación de AT y EL","Actuar",60),
    ("3.9.4","Plan de mejoramiento","Actuar",60),
]


def _validate_catalog():
    assert len(STANDARDS_CATALOG) == 60, f"El catálogo debe tener 60 registros, tiene {len(STANDARDS_CATALOG)}"
    codes = [c[0] for c in STANDARDS_CATALOG]
    assert len(set(codes)) == 60, "Hay códigos duplicados en el catálogo"
    for code, name, cat, group in STANDARDS_CATALOG:
        assert group in (7, 21, 60), f"Código {code}: group={group} inválido"
        assert cat in ("Planear", "Hacer", "Verificar", "Actuar"), f"Código {code}: categoría {cat!r} inválida"


_validate_catalog()


def seed_standards() -> dict:
    """
    Carga los estándares de la Resolución 0312 en la base de datos.
    Idempotente: verifica por código antes de insertar.
    Nunca elimina ni modifica registros existentes.
    Returns: {"inserted": N, "skipped": N}
    """
    inserted = 0
    skipped = 0
    for code, name, category, group in STANDARDS_CATALOG:
        exists = Standard.query.filter_by(code=code).first()
        if exists:
            skipped += 1
            continue
        db.session.add(Standard(code=code, name=name, category=category, group=group))
        inserted += 1
    if inserted > 0:
        db.session.commit()
    return {"inserted": inserted, "skipped": skipped}
