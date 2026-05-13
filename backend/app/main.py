"""
Punto de entrada de la API FastAPI.
Registra routers, configura CORS e inicializa la base de datos.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.database import init_db, SessionLocal
from app.routes import auth, companies, rats, user_companies, breaches, ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crea las tablas e inserta el usuario admin por defecto si no existe."""
    init_db()
    _seed_admin()
    yield


def _seed_admin():
    """Crea el usuario superadmin inicial si la BD está vacía."""
    from app.models.user import User, RolGlobal
    from app.core.security import get_password_hash

    db = SessionLocal()
    try:
        if not db.query(User).first():
            admin = User(
                username="admin",
                email="admin@ratmanager.cl",
                full_name="Administrador del Sistema",
                hashed_password=get_password_hash("admin1234"),
                is_active=True,
                rol_global=RolGlobal.SUPERADMIN.value,
            )
            db.add(admin)
            db.commit()
            print("✅ Superadmin creado: admin / admin1234")
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(rats.router)
app.include_router(user_companies.router)
app.include_router(breaches.router)
app.include_router(ai.router)


@app.get("/", tags=["Sistema"])
async def root():
    return {
        "sistema": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "estado": "operativo",
        "documentacion": "/docs",
    }


@app.get("/health", tags=["Sistema"])
async def health():
    return {"status": "ok"}
