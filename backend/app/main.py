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
from app.middleware.csrf import CSRFMiddleware
from app.routes import auth, companies, rats, user_companies, breaches, ai, rubros, tkt_solicitud_derecho, tkt_plantillas, tkt_reglas_asignacion, encargados_contrato, politica_transparencia, consentimientos, eipd, admin_tasks, feriados, asesor, admin_asesor, admin_companies, seguimiento, export_tkt, module_permissions
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
    """Crea el usuario superadmin inicial si la BD est├í vac├¡a y SEED_ADMIN=true."""
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
            print(f"Ô£à Superadmin creado: admin / {secret[:4]}***")
    finally:
        db.close()


def _seed_rubros():
    """Crea rubros y RATs sugeridos si la tabla est├í vac├¡a."""
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
        print(f"Ô£à {len(seed_data['rubros'])} rubros y sugerencias seedeados")
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
app.add_middleware(CSRFMiddleware)


class SecurityHeadersMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        await self.app(scope, receive, self._patch_send(send))

    def _patch_send(self, send):
        async def patched_send(message):
            if message.get("type") == "http.response.start":
                headers = dict(message.get("headers", []))
                headers[b"X-Content-Type-Options"] = b"nosniff"
                headers[b"X-Frame-Options"] = b"DENY"
                headers[b"X-XSS-Protection"] = b"1; mode=block"
                headers[b"Referrer-Policy"] = b"strict-origin-when-cross-origin"
                headers[b"Permissions-Policy"] = b"geolocation=(), microphone=(), camera=()"
                # Content-Security-Policy (Z-01): API no renderiza HTML
                # pero igual devolvemos CSP restrictiva para defense-in-depth.
                headers[b"Content-Security-Policy"] = (
                    b"default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
                )
                # Strict-Transport-Security (HSTS) — solo si HTTPS (Vercel)
                headers[b"Strict-Transport-Security"] = b"max-age=31536000; includeSubDomains"
                message = {**message, "headers": list(headers.items())}
            await send(message)
        return patched_send


app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "X-Request-ID",
        "Accept",
        "Origin",
    ],
    expose_headers=["X-Request-ID"],
)

# F3.1: Versionamiento API /api/v1/
# Mantenemos compatibilidad con los endpoints legacy (sin prefijo v1)
# durante un periodo de deprecacion. Los nuevos clientes deben usar /api/v1/.
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth.router)
v1_router.include_router(companies.router)
v1_router.include_router(rats.router)
v1_router.include_router(user_companies.router)
v1_router.include_router(breaches.router)
v1_router.include_router(ai.router)
v1_router.include_router(rubros.router)
v1_router.include_router(rubros.router_sugeridos)
v1_router.include_router(tkt_solicitud_derecho.router)
v1_router.include_router(tkt_plantillas.router)
v1_router.include_router(tkt_reglas_asignacion.router)
v1_router.include_router(encargados_contrato.router)
v1_router.include_router(politica_transparencia.router)
v1_router.include_router(seguimiento.router)
v1_router.include_router(consentimientos.router)
v1_router.include_router(eipd.router)
v1_router.include_router(admin_tasks.router)
v1_router.include_router(feriados.router)
v1_router.include_router(asesor.router)
v1_router.include_router(admin_asesor.router)
v1_router.include_router(admin_companies.router)
v1_router.include_router(export_tkt.router)
v1_router.include_router(module_permissions.router)

# Endpoints legacy (deprecated, mantener hasta migracion completa)
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(rats.router)
app.include_router(user_companies.router)
app.include_router(breaches.router)
app.include_router(ai.router)
app.include_router(rubros.router)
app.include_router(rubros.router_sugeridos)
app.include_router(tkt_solicitud_derecho.router)
app.include_router(tkt_plantillas.router)
app.include_router(tkt_reglas_asignacion.router)
app.include_router(encargados_contrato.router)
app.include_router(politica_transparencia.router)
app.include_router(seguimiento.router)
app.include_router(consentimientos.router)
app.include_router(eipd.router)
app.include_router(admin_tasks.router)
app.include_router(feriados.router)
app.include_router(asesor.router)
app.include_router(admin_asesor.router)
app.include_router(admin_companies.router)
app.include_router(export_tkt.router)
app.include_router(module_permissions.router)

# v1_router debe ir DESPUES de los routers legacy para que tome precedencia
# en el orden de matching (FastAPI matchea por orden de inclusion).
app.include_router(v1_router)


@app.get("/", tags=["Sistema"])
async def root():
    return {
        "sistema": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "api_versions": ["v1 (recomendado)", "legacy (deprecado, remover en Q1 2027)"],
        "estado": "operativo",
        "documentacion": "/docs",
    }


@app.get("/health", tags=["Sistema"])
async def health():
    return {"status": "ok"}


@app.get("/debug/oci", tags=["Debug"], include_in_schema=False)
async def debug_oci():
    from app.core.config import settings
    try:
        raw = os.environ.get("OCI_CONFIG", "")
        key_raw = os.environ.get("OCI_KEY_CONTENT", "")
        return {
            "oci_config_raw": raw[:100] + "..." if len(raw) > 100 else raw,
            "oci_config_empty": not bool(raw),
            "oci_config_parsed": settings.oci,
            "key_length": len(key_raw),
            "key_starts": key_raw[:30] if key_raw else None,
            "key_has_real_newlines": "\n" in key_raw,
            "key_has_literal_n": "\\n" in key_raw,
        }
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()[:500]}


@app.get("/debug/oci/test", tags=["Debug"], include_in_schema=False)
async def debug_oci_test():
    from app.core.config import settings
    try:
        from app.core.storage import OCIStorageBackend
    except Exception as e:
        import traceback
        return {"error": f"import failed: {e}", "traceback": traceback.format_exc()[:500]}

    try:
        cfg = settings.oci
    except Exception as e:
        import traceback
        return {"error": f"settings.oci failed: {e}", "traceback": traceback.format_exc()[:500]}

    if not cfg:
        return {"error": "no oci config"}

    try:
        backend = OCIStorageBackend(cfg, settings.OCI_KEY_CONTENT)
    except Exception as e:
        import traceback
        return {"error": f"backend init failed: {e}", "traceback": traceback.format_exc()[:500]}

    try:
        method = "GET"
        host = backend.host
        ns = backend.namespace
        bucket = backend.bucket
        path = f"/n/{ns}/b/{bucket}/o"

        signed = backend.signer.sign_headers(method, path, host)
        auth_header = signed.get("Authorization", "")

        # Build signing string for debugging
        date_value = signed.get("Date") or signed.get("date") or ""
        signing_string = "\n".join([
            f"(request-target): {method.lower()} {path}",
            f"date: {date_value}",
            f"host: {host}",
        ])

        url = f"{backend.base_url}{path}"
        import requests as r

        # Use PreparedRequest to see exactly what requests sends
        req = r.Request(method, url, headers=signed)
        prepared = req.prepare()
        actual_headers_sent = dict(prepared.headers)

        resp = r.get(url, headers=signed, timeout=10)

        return {
            "method": method,
            "host": host,
            "path": path,
            "url": url,
            "request_date": signed.get("Date") or signed.get("date"),
            "signing_string": signing_string,
            "authorization_first_120": auth_header[:120] + "...",
            "authorization_length": len(auth_header),
            "actual_headers_sent_host": actual_headers_sent.get("Host"),
            "actual_headers_sent_date": actual_headers_sent.get("Date"),
            "actual_headers_sent_authorization_first_80": actual_headers_sent.get("Authorization", "")[:80] + "...",
            "response_status": resp.status_code,
            "response_body_first_300": resp.text[:300],
        }
    except Exception as e:
        import traceback
        return {"error": f"request failed: {e}", "traceback": traceback.format_exc()[:500]}


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
