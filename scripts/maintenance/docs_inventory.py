# scripts/maintenance/docs_inventory.py
# Barrido documental automatizado — governance del proyecto Custodio RAT
# Detecta lock files, mojibake, drift de terminologia (APDP vs APDC),
# docs v1.9 vigentes, links Markdown rotos.
#
# Uso:
#   python scripts/maintenance/docs_inventory.py
#   python scripts/maintenance/docs_inventory.py --json
#   python scripts/maintenance/docs_inventory.py --check-links
#   python scripts/maintenance/docs_inventory.py --strict
#
# Salida:
#   - Reporte formateado (default) o JSON (--json)
#   - Exit code 0 = sin hallazgos
#   - Exit code 1 = hallazgos P0/P1 (bloqueantes)
#   - Exit code 2 = solo P2/P3 (warnings)

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
DOCS_ROOT = REPO_ROOT / "docs"
DOCS_OFICIALES = DOCS_ROOT / "documentacion_oficial"
VERSION_VIGENTE = "v1.9"

# Severidades
P0 = "P0"  # Bloqueante: lock files, links rotos a docs vigentes
P1 = "P1"  # Drift entre fuentes: versiones desincronizadas
P2 = "P2"  # Higiene: mojibake, APDP operativo
P3 = "P3"  # Mejora: docs sin regenerar, oportunidades de automatizacion

# Patrones
LOCK_FILE_PATTERN = re.compile(r"^~\$.+\.(docx|doc|xls|xlsx)$")
MOJIBAKE_PATTERN = re.compile(r"[ÃâðŸÂ]{3,}|ï¿½|Â")
# Terminos canonicos (ver skill doc-governance/SKILL.md)
# APDP solo permitido en archivos historicos declarados
ARCHIVOS_HISTORICOS = (
    "docs/consultoria/",
    "docs/auditorias/2026-06-",
    "docs/auditorias/2026-05-",
    "docs/SESSION_STATE.md",
    "docs/backlog_seguimiento.md",
    "docs/CLEANUP_2026-",
    "docs/BARRIDO_DOCUMENTAL.md",
)
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# Documentos v1.9 vigentes esperados
DOCS_V1_9_ESPERADOS = [
    "02_Requisitos_Custodio_RAT_Manager_v1.9.docx",
    "03_Historias_Usuario_Custodio_RAT_Manager_v1.9.docx",
    "04_Casos_de_Uso_Custodio_RAT_Manager_v1.9.docx",
    "06_Arquitectura_Software_Custodio_RAT_Manager_v1.9.docx",
    "08_API_REST_Custodio_RAT_Manager_v1.9.docx",
    "09_Backlog_Producto_Custodio_RAT_Manager_v1.9.docx",
    "10_Plan_QA_Custodio_RAT_Manager_v1.9.docx",
    "12_Manual_Tecnico_Custodio_RAT_Manager_v1.9.docx",
    "Matriz_Trazabilidad_Custodio_RAT_Manager_v1.9.docx",
]


def is_historico(path_relativo):
    """True si el archivo es historico y puede mantener APDP."""
    p = path_relativo.replace("\\", "/")
    return any(p.startswith(prefix) for prefix in ARCHIVOS_HISTORICOS)


def scan_lock_files():
    """P0 — Detecta lock files de Office (~$*.docx)."""
    hallazgos = []
    for md_docx in DOCS_ROOT.rglob("*"):
        if not md_docx.is_file():
            continue
        if LOCK_FILE_PATTERN.match(md_docx.name):
            hallazgos.append({
                "severidad": P0,
                "tipo": "lock_file",
                "archivo": str(md_docx.relative_to(REPO_ROOT)),
                "mensaje": f"Lock file detectado: {md_docx.name} (cerrar Word antes de commitear)",
            })
    return hallazgos


def scan_mojibake(archivos_md):
    """P2 — Detecta caracteres mojibake en .md."""
    hallazgos = []
    for md in archivos_md:
        try:
            text = md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            hallazgos.append({
                "severidad": P2,
                "tipo": "encoding_invalido",
                "archivo": str(md.relative_to(REPO_ROOT)),
                "mensaje": "Archivo no es UTF-8 valido",
            })
            continue
        # Ignorar lineas descriptivas en docs de governance (que mencionan mojibake)
        lineas = text.split("\n")
        for n, linea in enumerate(lineas, 1):
            # Heuristica: si la linea describe que es mojibake, ignorar
            lower = linea.lower()
            if any(kw in lower for kw in ["mojibake", "encoding", "Ã±", "Â ", "caracteres"]):
                # Verificar si es solo texto descriptivo
                if "detec" in lower or "identific" in lower or "busc" in lower or "reemplaz" in lower:
                    continue
            if MOJIBAKE_PATTERN.search(linea):
                hallazgos.append({
                    "severidad": P2,
                    "tipo": "mojibake",
                    "archivo": str(md.relative_to(REPO_ROOT)),
                    "linea": n,
                    "mensaje": f"Posible mojibake en linea {n}: {linea[:120].strip()}",
                })
    return hallazgos


def scan_terminologia(archivos_md):
    """P2 — Detecta uso de APDP en archivos operacionales.

    Excluye menciones dentro de bloques de codigo, tablas de homologacion
    o listas que documentan el cambio APDP -> APDC.
    """
    hallazgos = []
    for md in archivos_md:
        rel = str(md.relative_to(REPO_ROOT))
        if is_historico(rel):
            continue
        try:
            text = md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        # Remover bloques de codigo (inline `...` y fenced ```...```)
        text_sin_code = re.sub(r"`[^`]+`", "", text)
        text_sin_code = re.sub(r"```[\s\S]*?```", "", text_sin_code)

        count = text_sin_code.count("APDP")
        if count > 0:
            apdc_count = text_sin_code.count("APDC")
            hallazgos.append({
                "severidad": P2,
                "tipo": "terminologia_drift",
                "archivo": rel,
                "apdp": count,
                "apdc": apdc_count,
                "mensaje": f"APDP usado {count}x en archivo operacional (APDC: {apdc_count}x). Reemplazar APDP -> APDC.",
            })
    return hallazgos


def scan_version_vigente():
    """P1 — Detecta docs faltantes en v1.9 o docs sin v1.9 cuando deberian tenerlo."""
    hallazgos = []
    if not DOCS_OFICIALES.exists():
        hallazgos.append({
            "severidad": P1,
            "tipo": "carpeta_faltante",
            "archivo": "docs/documentacion_oficial/",
            "mensaje": "Carpeta docs/documentacion_oficial/ no existe",
        })
        return hallazgos

    existentes = {f.name for f in DOCS_OFICIALES.glob("*.docx") if f.is_file()}
    for esperado in DOCS_V1_9_ESPERADOS:
        if esperado not in existentes:
            hallazgos.append({
                "severidad": P1,
                "tipo": "doc_vigente_faltante",
                "archivo": f"docs/documentacion_oficial/{esperado}",
                "mensaje": f"Doc v1.9 esperado no encontrado: {esperado}",
            })
    return hallazgos


def scan_links_rotos(archivos_md):
    """P0 — Detecta links Markdown que apuntan a archivos inexistentes.

    Ignora links anotados con `*(por crear)*` en la misma linea
    (aspiracionales, no bugs).
    """
    hallazgos = []
    for md in archivos_md:
        try:
            text = md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = md.relative_to(REPO_ROOT)
        for n, linea in enumerate(text.split("\n"), 1):
            # Skip links aspiracionales marcados en la misma linea
            if re.search(r"\*\([Pp]or crear\)\*|\(por crear\)", linea):
                continue
            for match in LINK_PATTERN.finditer(linea):
                target = match.group(2)
                # Ignorar URLs externas, anchors puros y protocolos
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                # Resolver path relativo
                if target.startswith("/"):
                    target_path = REPO_ROOT / target.lstrip("/")
                else:
                    target_path = (md.parent / target).resolve()
                    target_path_str = str(target_path)
                    target_path_str = target_path_str.split("#")[0].split("?")[0]
                    target_path = Path(target_path_str)
                target_no_frag = str(target_path).split("#")[0]
                target_check = Path(target_no_frag)
                if not target_check.exists():
                    hallazgos.append({
                        "severidad": P0,
                        "tipo": "link_roto",
                        "archivo": str(rel),
                        "linea": n,
                        "link": target,
                        "mensaje": f"Link roto en linea {n}: [{match.group(1)}]({target})",
                    })
    return hallazgos


def scan_docs_no_vigentes():
    """P3 — Lista docs v1.6.5 y v1.0 que podrian regenerarse a v1.9."""
    hallazgos = []
    if not DOCS_OFICIALES.exists():
        return hallazgos
    for f in DOCS_OFICIALES.glob("*.docx"):
        if "v1.9" not in f.name:
            hallazgos.append({
                "severidad": P3,
                "tipo": "doc_no_vigente",
                "archivo": str(f.relative_to(REPO_ROOT)),
                "version": "v1.0" if "v1.0" in f.name else "otra",
                "mensaje": f"Doc no regenerado a v1.9: {f.name}",
            })
    return hallazgos


def imprimir_reporte(hallazgos, formato="text"):
    if formato == "json":
        print(json.dumps(hallazgos, indent=2, ensure_ascii=False))
        return

    # Agrupar por severidad
    por_severidad = {P0: [], P1: [], P2: [], P3: []}
    for h in hallazgos:
        por_severidad.setdefault(h["severidad"], []).append(h)

    print("=" * 70)
    print("  CUSTODIO RAT - Barrido Documental (v1.9)")
    print("=" * 70)
    print(f"Repo: {REPO_ROOT}")
    print(f"Version vigente esperada: {VERSION_VIGENTE}")
    print()

    total_por_severidad = {s: len(por_severidad[s]) for s in [P0, P1, P2, P3]}
    print("Resumen:")
    for sev in [P0, P1, P2, P3]:
        print(f"  [{sev}] {total_por_severidad[sev]} hallazgos")
    print()

    if not hallazgos:
        print("[OK] Sin hallazgos. Gobernanza documental limpia.")
        return

    for sev in [P0, P1, P2, P3]:
        items = por_severidad[sev]
        if not items:
            continue
        print("-" * 70)
        print(f"  [{sev}] {len(items)} hallazgos")
        print("-" * 70)
        for h in items:
            print(f"  - [{h['tipo']}] {h['archivo']}")
            if "linea" in h:
                print(f"    linea {h['linea']}: {h.get('link', '')}")
            print(f"    {h['mensaje']}")
            print()


def main():
    parser = argparse.ArgumentParser(description="Barrido documental automatizado de Custodio RAT")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    parser.add_argument("--check-links", action="store_true", help="Verificar links Markdown (lento)")
    parser.add_argument("--strict", action="store_true", help="Falla tambien por hallazgos P2/P3")
    args = parser.parse_args()

    if not DOCS_ROOT.exists():
        print(f"ERROR: {DOCS_ROOT} no existe", file=sys.stderr)
        return 2

    # Recolectar archivos .md
    archivos_md = sorted([p for p in DOCS_ROOT.rglob("*.md") if p.is_file()])

    hallazgos = []
    hallazgos.extend(scan_lock_files())
    hallazgos.extend(scan_mojibake(archivos_md))
    hallazgos.extend(scan_terminologia(archivos_md))
    hallazgos.extend(scan_version_vigente())
    if args.check_links:
        hallazgos.extend(scan_links_rotos(archivos_md))
    hallazgos.extend(scan_docs_no_vigentes())

    imprimir_reporte(hallazgos, formato="json" if args.json else "text")

    # Exit codes
    severidades_presentes = {h["severidad"] for h in hallazgos}
    if P0 in severidades_presentes or P1 in severidades_presentes:
        return 1
    if args.strict and (P2 in severidades_presentes or P3 in severidades_presentes):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())