"""
Punto de entrada de la API FastAPI.
Registra routers, configura CORS e inicializa la base de datos.
"""

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
from app.core.logging_config import setup_logging
from app.database.database import init_db, SessionLocal
from app.middleware.request_id import RequestIdMiddleware
from app.routes import auth, companies, rats, user_companies, breaches, ai, rubros, solicitudes_derecho, tkt_solicitud_derecho, encargados_contrato, politica_transparencia, consentimientos, eipd, admin_tasks, feriados
from app.services.scheduler import start_scheduler, stop_scheduler

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea las tablas e inserta el usuario admin por defecto si no existe."""
    if os.getenv("ENV") != "test":
        init_db()
        _seed_admin()
        _seed_rubros()
        start_scheduler()
    yield
    if os.getenv("ENV") != "test":
        stop_scheduler()


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
    import json
    import os
    from app.models.rubro import Rubro
    from app.models.rats_sugerido import RATSugerido

    db = SessionLocal()
    try:
        if db.query(Rubro).first():
            return

        seed_path = os.path.join(os.path.dirname(__file__), "data", "seed_rubros.json")
        with open(seed_path, "r", encoding="utf-8") as f:
            seed_data = json.load(f)

        for nombre, orden in seed_data["rubros"]:
            rubro = Rubro(nombre=nombre, orden=orden)
            db.add(rubro)

        db.commit()

        for nombre_rubro, sugerencias in seed_data["sugerencias"].items():
            rubro = db.query(Rubro).filter(Rubro.nombre == nombre_rubro).first()
            if not rubro:
                continue
            for sg in sugerencias:
                sugerencia = RATSugerido(rubro_id=rubro.id, **sg)
                db.add(sugerencia)

        db.commit()
        print(f"✅ {len(seed_data['rubros'])} rubros y sugerencias seedeados")
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

ALLOWED_ORIGINS = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
if not ALLOWED_ORIGINS:
    raise RuntimeError(
        "ALLOWED_ORIGINS env var is required. "
        "Example: ALLOWED_ORIGINS=https://custodio-qa.vercel.app,http://localhost:3000"
    )

app.add_middleware(RequestIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
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
app.include_router(consentimientos.router)
app.include_router(eipd.router)
app.include_router(admin_tasks.router)
app.include_router(feriados.router)


@app.get("/", tags=["Sistema"])
async def root():
    return {
        "sistema": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "estado": "operativo",
        "documentacion": "/docs",
    }


# debug endpoint removed


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
