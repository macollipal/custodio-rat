#!/usr/bin/env python3
"""
Pre-commit hook: enforce schema-migration sync.

Detecta cuando un commit agrega columnas o tablas en SQLAlchemy models
sin un companion .sql migration en backend/migrations/.

Uso:
    Como hook de pre-commit (via .git/hooks/pre-commit + .pre-commit-config.yaml)
    O manualmente:    python scripts/maintenance/schema_migration_sync.py

Exit code 0 = OK
Exit code 1 = bloquea el commit

Historia: este hook existe porque el 2026-07-07 el commit 76695ce agregó
telefono_dpo + representante_legal al modelo Company sin un .sql companion,
lo que rompió el endpoint GET /rats en producción con
`psycopg2.errors.UndefinedColumn: column companies.telefono_dpo does not exist`.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = REPO_ROOT / "backend" / "app" / "models"
MIGRATIONS_DIR = REPO_ROOT / "backend" / "migrations"

# Regex que detecta un mapped_column con un Column Type (String/Integer/Text/...)
# seguido (en cualquier línea) por un nombre (sin =) — heurística del nombre de columna.
# Aproximación: contar número de `mapped_column(...)` en la línea modificada.
ADDED_COLUMN_RE = re.compile(
    r"\+\s*(?:[a-zA-Z_][a-zA-Z0-9_]*:.*=.*)?\s*mapped_column\s*\(",
    re.MULTILINE,
)


def diff_files(ref_a: str, ref_b: str) -> list[str]:
    """Devuelve lista de paths cambiados entre ref_a y ref_b."""
    cmd = ["git", "diff", "--name-only", ref_a, ref_b]
    out = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def diff_for_file(ref_a: str, ref_b: str, path: str) -> str:
    """Devuelve el patch de un archivo entre ref_a y ref_b."""
    cmd = ["git", "diff", ref_a, ref_b, "--", path]
    out = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    return out.stdout


def detect_added_columns() -> list[tuple[str, str]]:
    """
    Compara HEAD con working tree (staged o unstaged).
    Devuelve lista de (model_file_path, evidence) donde evidence es un diff recortado
    que muestra que se agregó una columna.
    """
    # Staged + unstaged + HEAD~1 vs HEAD si staged
    # Usamos 'git diff HEAD' para ver staged + unstaged vs HEAD
    cmd = ["git", "diff", "HEAD"]
    out = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if out.returncode != 0 and not out.stdout:
        # initial commit
        cmd = ["git", "diff", "--cached"]
        out = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False)

    diff_text = out.stdout
    if not diff_text:
        return []

    findings = []
    current_file = None
    current_chunk: list[str] = []

    def flush():
        nonlocal current_chunk, current_file, findings
        if current_file and current_chunk:
            added_lines = "\n".join(current_chunk)
            if ADDED_COLUMN_RE.search(added_lines):
                # Trim chunk to first 25 lines for evidence
                preview = "\n".join(current_chunk[:25])
                if len(current_chunk) > 25:
                    preview += f"\n... ({len(current_chunk) - 25} more lines)"
                findings.append((current_file, preview))
        current_file = None
        current_chunk = []

    for line in diff_text.splitlines():
        if line.startswith("diff --git"):
            flush()
            # extract path
            m = re.search(r" b/(.+)$", line)
            current_file = m.group(1) if m else None
        elif line.startswith("@@"):
            current_chunk = []
        elif current_file and line.startswith("+") and not line.startswith("+++"):
            current_chunk.append(line)
        elif current_file and not line.startswith("+"):
            # boundary: reset chunk when we hit context (-) after additions
            # but only if we had additions
            if current_chunk:
                current_chunk = []
    flush()
    return findings


def main():
    parser = argparse.ArgumentParser(description="Schema migration sync check")
    parser.add_argument("--staged-only", action="store_true",
                        help="Solo diff staged (--cached)")
    args = parser.parse_args()

    # Use staged diff for pre-commit (more reliable than working tree vs HEAD)
    cmd = ["git", "diff", "--cached"]
    out = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, check=False)
    diff_text = out.stdout.decode("utf-8", errors="replace")

    if not diff_text:
        # Nothing staged → nothing to check
        return 0

    changed_files: list[str] = []
    current_file = None
    schema_changes: dict[str, list[str]] = {}
    for line in diff_text.splitlines():
        m = re.match(r"diff --git a/(.+?) b/(.+?)$", line)
        if m:
            # flush previous
            if current_file and current_file in schema_changes:
                pass  # already collected
            current_file = m.group(2)
            changed_files.append(current_file)
            continue
        if current_file and current_file.startswith("backend/app/models/") and current_file.endswith(".py"):
            if line.startswith("+") and not line.startswith("+++"):
                schema_changes.setdefault(current_file, []).append(line)
            elif line.startswith("@@"):
                schema_changes.setdefault(current_file, [])  # start new chunk

    # Filter to actual `mapped_column(...)` additions
    real_changes: dict[str, list[str]] = {}
    for path, lines in schema_changes.items():
        added_lines = "\n".join(lines)
        if ADDED_COLUMN_RE.search(added_lines):
            real_changes[path] = lines[:30]

    if not real_changes:
        return 0

    # Check if any migrations file was changed in same commit
    migrations_changed = [f for f in changed_files if f.startswith("backend/migrations/") and (f.endswith(".sql") or f.endswith(".py"))]
    apply_script_changed = [f for f in changed_files if f.startswith("backend/") and f.startswith("backend/apply_migration")]

    if migrations_changed or apply_script_changed:
        return 0

    # FAIL with clear error
    print("\n[FAIL] Schema migration sync violated:", file=sys.stderr)
    print(
        "\n  Detectaste un cambio de SCHEMA en SQLAlchemy models "
        "pero NO incluiste una migración SQL en backend/migrations/.",
        file=sys.stderr,
    )
    print(
        "\n  Esto es exactamente lo que pasó el 2026-07-07: el commit "
        "76695ce agregó telefono_dpo + representante_legal al modelo "
        "Company sin un .sql companion. La query contra companies falló "
        "en producción con `column companies.telefono_dpo does not exist`.",
        file=sys.stderr,
    )
    print("\n  Archivos modificados:", file=sys.stderr)
    for path in real_changes:
        print(f"    - {path}", file=sys.stderr)
    print("\n  Evidencia (líneas agregadas):", file=sys.stderr)
    for path, lines in real_changes.items():
        print(f"\n  --- {path} ---", file=sys.stderr)
        for ln in lines:
            print(f"    {ln}", file=sys.stderr)
    print(
        "\n  Remedio:\n"
        "    1. Crea backend/migrations/YYYY_MM_DD_NNN_<descripcion>.sql\n"
        "    2. Usa ALTER TABLE ... ADD COLUMN IF NOT EXISTS (idempotente)\n"
        "    3. Si no aplica migración, justifica con --no-schema-change:\n"
        "         git commit --no-verify   (solo si ES un cambio cosmético,\n"
        "                                    NUNCA para columnas reales)\n",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
