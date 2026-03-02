# User Profile App

## Estructura del Proyecto

```
user-profile/
├── backend/
│   ├── app.py                  # Punto de entrada (Flask factory)
│   ├── config.py               # Configuracion por entornos
│   ├── requirements.txt        # Dependencias Python
│   ├── models/
│   │   └── user.py             # Modelo User + UserRepository
│   ├── routes/
│   │   ├── auth.py             # POST /api/auth/login | change-password
│   │   └── profile.py          # GET/PUT /api/profile | /avatar
│   ├── services/
│   │   ├── auth_service.py     # Logica de autenticacion
│   │   └── profile_service.py  # Logica de perfil e imagenes
│   ├── utils/
│   │   ├── decorators.py       # @login_required con JWT
│   │   └── file_handler.py     # Validacion, resize y guardado de avatares
│   └── uploads/                # Carpeta auto-generada para fotos
└── frontend/
    ├── index.html              # Pagina de login
    ├── profile.html            # Pagina de perfil
    ├── css/
    │   └── styles.css          # Estilos completos
    └── js/
        ├── auth.js             # Logica de login
        └── profile.js          # Logica del perfil

```

## Instalacion

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Luego abre `frontend/index.html` en tu navegador (o sirvelo con Live Server en VS Code).

## Credenciales de prueba

| Campo | Valor |
|-------|-------|
| Email | demo@example.com |
| Contrasena | demo1234 |

## Endpoints de la API

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | /api/auth/login | Iniciar sesion |
| POST | /api/auth/change-password | Cambiar contrasena (auth) |
| GET | /api/profile | Obtener perfil (auth) |
| PUT | /api/profile | Editar informacion (auth) |
| POST | /api/profile/avatar | Subir foto (auth) |
| DELETE | /api/profile/avatar | Eliminar foto (auth) |
| GET | /api/profile/avatar/<file> | Servir imagen |

## Como escalar a produccion

1. **Base de datos**: Reemplaza `UserRepository` con SQLAlchemy + PostgreSQL
2. **Almacenamiento**: Usa AWS S3 o similar en lugar de `uploads/`
3. **Autenticacion**: Agrega refresh tokens y revocacion de JWT
4. **Variables de entorno**: Crea un `.env` con SECRET_KEY y JWT_SECRET_KEY
5. **Deploy**: Usa Gunicorn + Nginx, o despliega en Railway / Render
