# SSTcloud

Plataforma web para la gestión del **Sistema de Gestión de Seguridad y Salud en el Trabajo (SG-SST)** para empresas colombianas, basada en la **Resolución 0312 de 2019 del Ministerio del Trabajo**.

---

## ¿Qué es SSTcloud?

SSTcloud permite a las empresas colombianas gestionar y demostrar su cumplimiento con los estándares mínimos del SG-SST de forma digital. La plataforma clasifica automáticamente a cada empresa según la resolución, le muestra exactamente qué estándares debe cumplir, y le permite subir los documentos de evidencia para cada uno.

---

## Funcionalidades

- **Autenticación segura** con JWT
- **Registro de empresa** con clasificación automática según la Resolución 0312
- **Lista personalizada de estándares** — cada empresa ve solo los que le aplican por ley
- **Subida de evidencias** por estándar (PDF, DOCX, XLSX — máx. 10 MB)
- **Dashboard de cumplimiento** con porcentaje en tiempo real y nivel de estado
- **Perfil de usuario** con foto de perfil

---

## Clasificación automática — Resolución 0312 de 2019

La plataforma determina automáticamente cuántos estándares aplican a cada empresa:

| Trabajadores | Nivel de riesgo ARL | Estándares requeridos |
|:---:|:---:|:---:|
| ≤ 10 | I, II o III | **7** |
| 11 a 50 | I, II o III | **21** |
| > 50 | Cualquiera | **60** |
| Cualquier tamaño | IV o V | **60** |

Una empresa con 25 trabajadores y riesgo II ve exactamente **21 estándares**. Una empresa con 80 trabajadores y riesgo V ve los **60 estándares completos**. Cada empresa trabaja únicamente con lo que le corresponde por ley.

---

## Niveles de cumplimiento

| Porcentaje | Estado |
|:---:|:---:|
| 0% — 59% | 🔴 Crítico |
| 60% — 84% | 🟡 Moderado |
| 85% — 99% | 🟢 Aceptable |
| 100% | ✅ Excelente |

---

## Tech Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3 + Flask |
| ORM | Flask-SQLAlchemy |
| Autenticación | JWT (flask-jwt-extended) |
| Base de datos | SQLite (desarrollo) / PostgreSQL (producción) |
| Archivos | Pillow (imágenes) + manejo nativo (documentos) |
| API | REST + Blueprint structure + Service layer |

---

## Estructura del proyecto

```
user-profile/
└── backend/
    ├── app.py                     # Factory pattern — punto de entrada
    ├── config.py                  # Configuración por entornos
    ├── database.py                # Instancia SQLAlchemy
    ├── requirements.txt
    │
    ├── models/
    │   ├── user.py                # Usuario con perfil y avatar
    │   ├── company.py             # Empresa + clasificación Res. 0312
    │   ├── standard.py            # Catálogo de estándares SG-SST
    │   └── evidence.py            # Archivos de evidencia por estándar
    │
    ├── routes/
    │   ├── auth.py                # POST /api/auth/login | change-password
    │   ├── profile.py             # GET/PUT /api/profile | /avatar
    │   └── sst.py                 # Endpoints SG-SST (empresa, estándares, evidencias)
    │
    ├── services/
    │   ├── auth_service.py        # Lógica de autenticación
    │   ├── profile_service.py     # Lógica de perfil e imágenes
    │   ├── sst_service.py         # Lógica SG-SST y cumplimiento
    │   └── seed_service.py        # Carga inicial de 60 estándares (idempotente)
    │
    └── utils/
        ├── decorators.py          # @login_required con JWT
        └── file_handler.py        # Avatares (PNG/JPG) + Evidencias (PDF/DOCX/XLSX)
```

---

## API Endpoints

### Autenticación
| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/auth/login` | Iniciar sesión |
| POST | `/api/auth/change-password` | Cambiar contraseña |

### Perfil
| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/profile` | Obtener perfil |
| PUT | `/api/profile` | Actualizar perfil |
| POST | `/api/profile/avatar` | Subir foto de perfil |
| DELETE | `/api/profile/avatar` | Eliminar foto de perfil |

### SG-SST
| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/sst/company` | Registrar empresa |
| GET | `/api/sst/company` | Obtener datos de empresa |
| PUT | `/api/sst/company` | Actualizar empresa |
| GET | `/api/sst/standards` | Listar estándares aplicables |
| POST | `/api/sst/standards/<id>/evidence` | Subir evidencia |
| GET | `/api/sst/standards/<id>/evidence` | Ver evidencia de un estándar |
| DELETE | `/api/sst/evidence/<id>` | Eliminar evidencia |
| GET | `/api/sst/compliance` | Dashboard de cumplimiento |

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO/backend

# 2. Crear y activar entorno virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Correr el servidor
python app.py
```

Al arrancar por primera vez, el servidor carga automáticamente los **60 estándares** de la Resolución 0312 en la base de datos y crea el usuario demo.

---

## Credenciales demo

```
Email:    demo@example.com
Password: demo1234
```

---

## Estado del proyecto

- [x] Autenticación JWT
- [x] Perfil de usuario con avatar
- [x] Modelo de empresa con clasificación automática Res. 0312
- [x] Catálogo de 60 estándares SG-SST (seed automático)
- [x] Subida y gestión de evidencias por estándar
- [x] Cálculo de porcentaje de cumplimiento en tiempo real
- [x] API REST completa y probada
- [ ] Frontend SSTcloud (en desarrollo)

---

## Roadmap

```
Fase 1 — Backend    ✅ Completo
Fase 2 — Frontend   🔄 En desarrollo
Fase 3 — Reportes   📋 Pendiente
Fase 4 — Multi-usuario por empresa  📋 Pendiente
```
