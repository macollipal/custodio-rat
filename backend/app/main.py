"""
Punto de entrada de la API FastAPI.
Registra routers, configura CORS e inicializa la base de datos.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
from app.database.database import init_db, SessionLocal
from app.routes import auth, companies, rats, user_companies, breaches, ai, rubros, solicitudes_derecho, tkt_solicitud_derecho, encargados_contrato, politica_transparencia


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea las tablas e inserta el usuario admin por defecto si no existe."""
    init_db()
    _seed_admin()
    _seed_rubros()
    yield


def _seed_admin():
    """Crea el usuario superadmin inicial si la BD está vacía y SEED_ADMIN=true."""
    import os
    if os.getenv("SEED_ADMIN", "").lower() != "true":
        return
    from app.models.user import User, RolGlobal
    from app.core.security import get_password_hash

    secret = os.getenv("SEED_ADMIN_PASSWORD")
    if not secret:
        print("⚠️ SEED_ADMIN=true pero no se definió SEED_ADMIN_PASSWORD — omitiendo seed")
        return

    db = SessionLocal()
    try:
        if not db.query(User).first():
            admin = User(
                username="admin",
                email="admin@ratmanager.cl",
                full_name="Administrador del Sistema",
                hashed_password=get_password_hash(secret),
                is_active=True,
                rol_global=RolGlobal.SUPERADMIN.value,
            )
            db.add(admin)
            db.commit()
            print(f"✅ Superadmin creado: admin / {secret[:4]}***")
    finally:
        db.close()


def _seed_rubros():
    """Crea rubros y RATs sugeridos si la tabla está vacía."""
    from app.models.rubro import Rubro
    from app.models.rats_sugerido import RATSugerido

    db = SessionLocal()
    try:
        if db.query(Rubro).first():
            return

        rubros_data = [
            ("Salud", 1),
            ("Retail", 2),
            ("Educación", 3),
            ("Financiero", 4),
            ("Tecnología", 5),
            ("Construcción", 6),
            ("Transportes", 7),
            ("Telecomunicaciones", 8),
            ("Turismo", 9),
            ("Agronomía", 10),
            ("Minería", 11),
            ("Energía", 12),
            ("Servicios profesionales", 13),
            ("Juegos de azar", 14),
            ("Aseguradoras", 15),
            ("Administraciones públicas", 16),
            ("Medios de comunicación", 17),
            ("Otro", 18),
        ]

        sugerencias_data = {
            "Salud": [
                {"nombre_proceso": "Gestión de pacientes", "categoria_datos": "Datos identificativos, Datos de salud", "categoria_titulares": "Pacientes", "finalidad": "Prestacion de servicios de salud", "base_legal": "Consentimiento del titular", "plazo_retencion": "15 años después del último contacto", "datos_sensibles": True, "evaluacion_impacto": True},
                {"nombre_proceso": "Gestión de personal médico", "categoria_datos": "Datos identificativos, Datos laborales", "categoria_titulares": "Empleados", "finalidad": "Cumplimiento de obligaciones laborales", "base_legal": "Obligación legal", "plazo_retencion": "5 años después del término de la relación laboral", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Investigación clínica", "categoria_datos": "Datos identificativos, Datos de salud, Datos biométricos", "categoria_titulares": "Pacientes, voluntarios", "finalidad": "Investigación y desarrollo", "base_legal": "Consentimiento del titular", "plazo_retencion": "20 años", "datos_sensibles": True, "evaluacion_impacto": True},
                {"nombre_proceso": "Gestión de seguros de salud", "categoria_datos": "Datos identificativos, Datos de salud, Datos financieros", "categoria_titulares": "Asegurados", "finalidad": "Gestión de pólizas y reclamos", "base_legal": "Ejecución de contrato", "plazo_retencion": "10 años", "datos_sensibles": True, "evaluacion_impacto": False},
                {"nombre_proceso": "Videovigilancia en instalaciones", "categoria_datos": "Datos biométricos (imagen)", "categoria_titulares": "Pacientes, visitantes", "finalidad": "Seguridad de instalaciones", "base_legal": "Interés legítimo", "plazo_retencion": "30 días", "datos_sensibles": True, "evaluacion_impacto": False},
            ],
            "Retail": [
                {"nombre_proceso": "Gestión de clientes", "categoria_datos": "Datos identificativos, Datos financieros", "categoria_titulares": "Clientes", "finalidad": "Comercialización de productos", "base_legal": "Consentimiento del titular", "plazo_retencion": "5 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Gestión de proveedores", "categoria_datos": "Datos identificativos, Datos financieros", "categoria_titulares": "Proveedores", "finalidad": "Gestión de compras y pagos", "base_legal": "Ejecución de contrato", "plazo_retencion": "5 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Marketing y publicidad", "categoria_datos": "Datos identificativos, Datos de contacto", "categoria_titulares": "Clientes, potenciales clientes", "finalidad": "Promoción de productos y servicios", "base_legal": "Consentimiento del titular", "plazo_retencion": "3 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Gestión de garantías", "categoria_datos": "Datos identificativos, Datos de compra", "categoria_titulares": "Clientes", "finalidad": "Gestión de garantías y devoluciones", "base_legal": "Ejecución de contrato", "plazo_retencion": "3 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Control de acceso a tiendas", "categoria_datos": "Datos biométricos (imagen)", "categoria_titulares": "Empleados, visitantes", "finalidad": "Seguridad y control de inventarios", "base_legal": "Interés legítimo", "plazo_retencion": "30 días", "datos_sensibles": True, "evaluacion_impacto": False},
            ],
            "Educación": [
                {"nombre_proceso": "Gestión académica de estudiantes", "categoria_datos": "Datos identificativos, Datos académicos, Datos de contacto", "categoria_titulares": "Estudiantes", "finalidad": "Gestión académica y administrativa", "base_legal": "Consentimiento del titular", "plazo_retencion": "10 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Gestión de personal docente", "categoria_datos": "Datos identificativos, Datos laborales", "categoria_titulares": "Docentes", "finalidad": "Cumplimiento de obligaciones laborales", "base_legal": "Obligación legal", "plazo_retencion": "5 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Control de asistencia y notas", "categoria_datos": "Datos identificativos, Datos académicos", "categoria_titulares": "Estudiantes", "finalidad": "Seguimiento del desempeño académico", "base_legal": "Interés legítimo", "plazo_retencion": "5 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Becas y ayudas económicas", "categoria_datos": "Datos identificativos, Datos financieros, Datos socioeconómicos", "categoria_titulares": "Estudiantes", "finalidad": "Gestión de becas", "base_legal": "Consentimiento del titular", "plazo_retencion": "10 años", "datos_sensibles": True, "evaluacion_impacto": False},
                {"nombre_proceso": "Videoconferencia y clases online", "categoria_datos": "Datos identificativos, Datos de contacto, Imagen", "categoria_titulares": "Estudiantes, docentes", "finalidad": "Educación a distancia", "base_legal": "Consentimiento del titular", "plazo_retencion": "1 año", "datos_sensibles": False, "evaluacion_impacto": False},
            ],
            "Financiero": [
                {"nombre_proceso": "Gestión de clientes y cuentas", "categoria_datos": "Datos identificativos, Datos financieros", "categoria_titulares": "Clientes", "finalidad": "Prestación de servicios financieros", "base_legal": "Ejecución de contrato", "plazo_retencion": "10 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Prevención de lavado de activos", "categoria_datos": "Datos identificativos, Datos financieros", "categoria_titulares": "Clientes", "finalidad": "Cumplimiento normativo AML/KYC", "base_legal": "Obligación legal", "plazo_retencion": "10 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Gestión de riesgos crediticios", "categoria_datos": "Datos identificativos, Datos financieros", "categoria_titulares": "Clientes", "finalidad": "Evaluación de riesgo crediticio", "base_legal": "Interés legítimo", "plazo_retencion": "5 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Marketing y promoción de productos", "categoria_datos": "Datos identificativos, Datos de contacto", "categoria_titulares": "Clientes, potenciales clientes", "finalidad": "Comercialización de productos financieros", "base_legal": "Consentimiento del titular", "plazo_retencion": "3 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Gestión de cobros y morosidad", "categoria_datos": "Datos identificativos, Datos financieros", "categoria_titulares": "Clientes", "finalidad": "Gestión de deuda", "base_legal": "Interés legítimo", "plazo_retencion": "5 años", "datos_sensibles": False, "evaluacion_impacto": False},
            ],
            "Tecnología": [
                {"nombre_proceso": "Gestión de usuarios de plataforma", "categoria_datos": "Datos identificativos, Datos de contacto", "categoria_titulares": "Usuarios", "finalidad": "Prestación de servicios digitales", "base_legal": "Consentimiento del titular", "plazo_retencion": "3 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Análisis de comportamiento", "categoria_datos": "Datos identificativos, Datos de navegación", "categoria_titulares": "Usuarios", "finalidad": "Mejora de productos y experiencia", "base_legal": "Consentimiento del titular", "plazo_retencion": "2 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Soporte técnico", "categoria_datos": "Datos identificativos, Datos técnicos", "categoria_titulares": "Clientes, usuarios", "finalidad": "Atención de soporte", "base_legal": "Ejecución de contrato", "plazo_retencion": "3 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Gestión de empleados tecnológicos", "categoria_datos": "Datos identificativos, Datos laborales", "categoria_titulares": "Empleados", "finalidad": "Gestión de recursos humanos", "base_legal": "Obligación legal", "plazo_retencion": "5 años", "datos_sensibles": False, "evaluacion_impacto": False},
                {"nombre_proceso": "Videovigilancia en data centers", "categoria_datos": "Datos biométricos (imagen)", "categoria_titulares": "Visitantes, empleados", "finalidad": "Seguridad física", "base_legal": "Interés legítimo", "plazo_retencion": "30 días", "datos_sensibles": True, "evaluacion_impacto": False},
            ],
        }

        # Crear rubros
        for nombre, orden in rubros_data:
            rubro = Rubro(nombre=nombre, orden=orden)
            db.add(rubro)

        db.commit()

        # Buscar rubro_id para sugerencias_data
        for nombre_rubro, sugerencias in sugerencias_data.items():
            rubro = db.query(Rubro).filter(Rubro.nombre == nombre_rubro).first()
            if not rubro:
                continue
            for sg in sugerencias:
                sugerencia = RATSugerido(rubro_id=rubro.id, **sg)
                db.add(sugerencia)

        db.commit()
        print(f"✅ {len(rubros_data)} rubros y sugerencias seedeados")
    finally:
        db.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=429,
        content={"detail": "Demasiados intentos. Intente nuevamente en un minuto."},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(rats.router)
app.include_router(user_companies.router)
app.include_router(breaches.router)
app.include_router(ai.router)
app.include_router(rubros.router)
app.include_router(rubros.router_sugeridos)
app.include_router(solicitudes_derecho.router)
app.include_router(tkt_solicitud_derecho.router)
app.include_router(encargados_contrato.router)
app.include_router(politica_transparencia.router)


@app.get("/", tags=["Sistema"])
async def root():
    return {
        "sistema": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "estado": "operativo",
        "documentacion": "/docs",
    }


@app.get("/debug/env", tags=["Sistema"])
async def debug_env():
    """Debug endpoint - muestra vars de entorno (sin passwords)."""
    from app.core.config import settings
    return {
        "DATABASE_URL_set": bool(settings.DATABASE_URL),
        "DATABASE_URL_host": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else "EMPTY",
        "SECRET_KEY_set": bool(settings.SECRET_KEY),
        "ENVIRONMENT": settings.ENVIRONMENT,
    }


@app.get("/health/db", tags=["Sistema"])
async def health_db():
    from app.core.config import settings
    from sqlalchemy import text
    import time

    db_info = {
        "engine": "postgresql",
        "url": settings.DATABASE_URL.split("@")[1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL,
    }

    start = time.time()
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_info["status"] = "ok"
        db_info["latency_ms"] = round((time.time() - start) * 1000, 1)
    except Exception as e:
        db_info["status"] = "error"
        db_info["error"] = str(e)

    return db_info
