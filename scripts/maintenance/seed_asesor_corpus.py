"""
Seed script: Populate the Asesor corpus with legal documentation.

This script populates the RAG corpus with the Custodio knowledge base:
  - Ley 21.719 reference content
  - Manuals (que_es_rat, MANUAL_USUARIO, CASO_ESTUDIO)
  - Use cases (CASO_01 through CASO_06)

Usage:
  Local (in-process indexer, no OCI needed):
    python seed_asesor_corpus.py local

  QA (via API — uploads to OCI, then indexes):
    python seed_asesor_corpus.py qa

  Prod (via API):
    python seed_asesor_corpus.py prod

Environment (local mode):
  DATABASE_URL, COHERE_API_KEY (or GROQ_API_KEY for embeddings)

Environment (QA/prod mode via API):
  .env file in backend/ with: DATABASE_URL
  Superadmin credentials via --user / --password or defaults
"""

import argparse
import os
import shutil
import sys
import json
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
DOCS_DIR = BACKEND_DIR.parent / "docs"
CORPUS_DIR = BACKEND_DIR / "data" / "asesor_corpus"

SUPERADMIN_CANDIDATES = [
    ("superadmin", "Admin1234!"),
    ("admin", "Admin1234!"),
    ("admin", "admin1234"),
]

API_CONFIGS = {
    "qa": {
        "base": "https://custodio-api-qa.vercel.app",
    },
    "prod": {
        "base": "https://custodio-api-prod.vercel.app",
    },
}

CORPUS_FILES = [
    ("manuales", "que_es_rat.md"),
    ("manuales", "MANUAL_USUARIO.md"),
    ("manuales", "CASO_ESTUDIO.md"),
    ("manuales", "MANUAL_PRUEBAS.md"),
    ("casos_de_uso", "CASO_01_Onboarding_Primera_Empresa.md"),
    ("casos_de_uso", "CASO_02_Crear_Primer_Proceso_RAT.md"),
    ("casos_de_uso", "CASO_03_Plantillas_Inteligentes.md"),
    ("casos_de_uso", "CASO_04_Deteccion_Incumplimiento.md"),
    ("casos_de_uso", "CASO_05_Registrar_Brecha_Seguridad.md"),
    ("casos_de_uso", "CASO_06_Exportar_Evidencia_Auditoria.md"),
    ("casos_de_uso", "asesor", "CASO_01_Onboarding_Primera_Empresa.md"),
    ("casos_de_uso", "asesor", "CASO_02_Crear_Primer_Proceso_RAT.md"),
    ("casos_de_uso", "asesor", "CASO_03_Plantillas_Inteligentes.md"),
    ("casos_de_uso", "asesor", "CASO_04_Deteccion_Incumplimiento.md"),
    ("arquitectura", "FLUJO_DATOS.md"),
]


def _login(client: "httpx.Client", base_url: str, username: str, password: str) -> str:
    r = client.post(
        f"{base_url}/auth/login",
        json={"username": username, "password": password},
    )
    if r.status_code != 200:
        raise RuntimeError(f"Login failed {username} → {r.status_code}: {r.text[:200]}")
    return r.json()["access_token"]


def run_local() -> None:
    sys.path.insert(0, str(BACKEND_DIR))
    os.chdir(BACKEND_DIR)

    from app.database.database import SessionLocal
    from app.services.asesor_indexer import index_corpus, list_corpus_files

    CORPUS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[*] Copying docs to {CORPUS_DIR}...")
    copied = 0
    for parts in CORPUS_FILES:
        src = DOCS_DIR.joinpath(*parts)
        if not src.exists():
            print(f"  [SKIP] {src} — not found")
            continue
        dst = CORPUS_DIR / src.name
        shutil.copy2(src, dst)
        print(f"  [COPY] {src.name}")
        copied += 1

    if copied == 0:
        print("[!] No files copied — check CORPUS_FILES paths")
        return

    print(f"\n[*] Running indexer (local mode, in-process)...")
    db = SessionLocal()
    try:
        result = index_corpus(db, force=True)
        print(f"\n[*] Indexer result:")
        print(f"    indexed : {result['indexed']}")
        print(f"    skipped : {result['skipped']}")
        print(f"    errors  : {len(result['errors'])}")
        for err in result.get("errors", [])[:5]:
            print(f"      - {err}")
        print(f"    duration: {result['duration_ms']}ms")
        print(f"    provider: {result.get('provider', 'unknown')}")
    finally:
        db.close()


def run_api(mode: str, username: str, password: str) -> None:
    try:
        import httpx
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx"])
        import httpx

    cfg = API_CONFIGS[mode]
    base = cfg["base"]

    print(f"[*] Corpus seed via API — mode={mode} base={base}")

    client = httpx.Client(timeout=60.0)
    try:
        token = _login(client, base, username, password)
        headers = {"Authorization": f"Bearer {token}"}

        uploaded = 0
        skipped = 0
        for parts in CORPUS_FILES:
            src = DOCS_DIR.joinpath(*parts)
            if not src.exists():
                print(f"  [SKIP] {src} — not found")
                skipped += 1
                continue

            content = src.read_text(encoding="utf-8")
            files = {"file": (src.name, content.encode("utf-8"), "text/markdown")}
            r = client.post(
                f"{base}/admin/asesor/upload",
                headers=headers,
                files=files,
            )
            if r.status_code == 200:
                data = r.json()
                print(f"  [OK]   {src.name} → doc_id={data.get('document_id', '?')} chunks={data.get('chunks_indexed', 0)}")
                uploaded += 1
            elif r.status_code == 422 and "ya existe" in r.text:
                print(f"  [SKIP] {src.name} — ya existe en corpus")
                skipped += 1
            else:
                print(f"  [FAIL] {src.name} → {r.status_code}: {r.text[:150]}")
    finally:
        client.close()

    print(f"\n[*] Triggering reindex (force=True)...")
    client = httpx.Client(timeout=120.0)
    try:
        token = _login(client, base, username, password)
        headers = {"Authorization": f"Bearer {token}"}
        r = client.post(
            f"{base}/admin/asesor/index",
            headers=headers,
            json={"paths": [], "force": True},
        )
        if r.status_code == 200:
            result = r.json()
            print(f"\n[*] Indexer result:")
            print(f"    indexed : {result['indexed']}")
            print(f"    skipped : {result['skipped']}")
            print(f"    errors  : {len(result['errors'])}")
            for err in result.get("errors", [])[:5]:
                print(f"      - {err}")
            print(f"    duration: {result['duration_ms']}ms")
        else:
            print(f"  [FAIL] index → {r.status_code}: {r.text[:200]}")
    finally:
        client.close()

    print(f"\n[*] Summary: {uploaded} uploaded, {skipped} skipped")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Asesor corpus with documentation")
    parser.add_argument("mode", choices=["local", "qa", "prod"], default="local",
                        nargs="?")
    parser.add_argument("--user", default="admin", help="Superadmin username (qa/prod)")
    parser.add_argument("--password", default="Admin1234!", help="Superadmin password (qa/prod)")
    args = parser.parse_args()

    print("=" * 60)
    print(f"ASESOR CORPUS SEED — mode={args.mode}")
    print("=" * 60)

    if args.mode == "local":
        run_local()
    else:
        run_api(args.mode, args.user, args.password)


if __name__ == "__main__":
    main()
