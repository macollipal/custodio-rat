# scripts/maintenance/health_check.py
# Runner local para auditar salud general del repositorio
# Uso: python scripts/maintenance/health_check.py

import subprocess
import sys
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def run_cmd(cmd, description):
    print(f"\n{'='*60}")
    print(f"  {description}")
    print('='*60)
    result = subprocess.run(cmd, shell=True, cwd=REPO_ROOT, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout[:2000])
    if result.stderr:
        print(result.stderr[:500], file=sys.stderr)
    return result.returncode == 0


def check_git_status():
    print(f"\n{'='*60}")
    print("  1. Git status — archivos sin trackear o modificados")
    print('='*60)
    result = subprocess.run("git status --short", shell=True, cwd=REPO_ROOT, capture_output=True, text=True)
    if result.stdout.strip():
        print(result.stdout)
        return False
    print("OK: working tree limpio")
    return True


def check_branch():
    print(f"\n{'='*60}")
    print("  2. Rama actual")
    print('='*60)
    result = subprocess.run("git rev-parse --abbrev-ref HEAD", shell=True, cwd=REPO_ROOT, capture_output=True, text=True)
    branch = result.stdout.strip()
    print(f"Rama: {branch}")
    if branch not in ['main', 'develop', 'qa']:
        print("WARNING: No es una rama protected (main/develop/qa)")
    return True


def check_gitleaks():
    print(f"\n{'='*60}")
    print("  3. Gitleaks — secretos en codigo")
    print('='*60)
    result = subprocess.run("gitleaks detect --source . --verbose --no-color", shell=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        print("ALERTA: Gitleaks detecto secretos o patrones sospechosos")
        return False
    print("OK: No se detectaron secretos")
    return True


def check_precommit():
    print(f"\n{'='*60}")
    print("  4. Pre-commit hooks")
    print('='*60)
    result = subprocess.run("pre-commit run --all-files", shell=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        print("ALERTA: Pre-commit detecto issues")
        return False
    print("OK: Todos los hooks pasaron")
    return True


def check_docs():
    print(f"\n{'='*60}")
    print("  5. Archivos de documentacion")
    print('='*60)
    docs = [
        "README.md",
        "CHANGELOG.md",
        "SECURITY.md",
        "docs/CLEANUP_2026-07-03.md",
    ]
    missing = []
    for doc in docs:
        path = REPO_ROOT / doc
        if not path.exists():
            missing.append(doc)
        else:
            print(f"OK: {doc}")
    if missing:
        print(f"MISSING: {', '.join(missing)}")
        return False
    return True


def check_skills():
    print(f"\n{'='*60}")
    print("  6. Skills —盘点")
    print('='*60)
    skills_dir = REPO_ROOT / ".opencode" / "skills"
    if not skills_dir.exists():
        print("FALLA: .opencode/skills/ no existe")
        return False
    skills = [d.name for d in skills_dir.iterdir() if d.is_dir()]
    print(f"Total skills: {len(skills)}")
    for s in sorted(skills):
        print(f"  - {s}")
    return True


def check_structure():
    print(f"\n{'='*60}")
    print("  7. Estructura de carpetas principales")
    print('='*60)
    folders = [
        "backend/app",
        "backend/tests",
        "backend/scripts",
        "frontend-next/app",
        "frontend-next/components",
        "docs",
        ".github/workflows",
    ]
    all_ok = True
    for folder in folders:
        path = REPO_ROOT / folder
        if path.exists():
            print(f"OK: {folder}")
        else:
            print(f"MISSING: {folder}")
            all_ok = False
    return all_ok


def main():
    print("="*60)
    print("  CUSTODIO RAT - Health Check")
    print("="*60)
    print(f"Repo: {REPO_ROOT}")

    checks = [
        ("Working tree limpio", check_git_status),
        ("Rama actual", check_branch),
        ("Docs obligatorias", check_docs),
        ("Skills", check_skills),
        ("Estructura", check_structure),
    ]

    results = []
    for name, fn in checks:
        try:
            ok = fn()
            results.append((name, ok))
        except Exception as e:
            print(f"ERROR en {name}: {e}")
            results.append((name, False))

    print("\n" + "="*60)
    print("  RESUMEN")
    print("="*60)
    all_ok = True
    for name, ok in results:
        status = "OK" if ok else "WARNING"
        print(f"  [{status}] {name}")
        if not ok:
            all_ok = False

    print("\n" + "="*60)
    if all_ok:
        print("  HEALTH CHECK: PASSED")
        print("="*60)
        return 0
    else:
        print("  HEALTH CHECK: ATTENTION NEEDED")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
