# backend/scripts/security_audit.py
# Runner local para auditoria de seguridad
# Uso: python scripts/security_audit.py

import subprocess
import sys
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def run(cmd, description):
    print(f"\n{'='*60}")
    print(f"  {description}")
    print('='*60)
    result = subprocess.run(cmd, shell=True, cwd=REPO_ROOT)
    return result.returncode == 0


def check_precommit_installed():
    print(f"\n{'='*60}")
    print("  1. Verificando pre-commit instalado")
    print('='*60)
    result = subprocess.run("pre-commit --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("PRE-COMMIT NO INSTALADO")
        print("Instalar con: pip install pre-commit")
        return False
    print(f"OK: {result.stdout.decode().strip()}")
    return True


def check_gitleaks():
    print(f"\n{'='*60}")
    print("  2. Verificando gitleaks")
    print('='*60)
    result = subprocess.run("gitleaks --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("GITLEAKS NO INSTALADO")
        print("Instalar desde: https://github.com/gitleaks/gitleaks")
        return False
    print(f"OK: {result.stdout.decode().strip()}")
    return True


def run_gitleaks():
    print(f"\n{'='*60}")
    print("  3. Ejecutando gitleaks (dry-run)")
    print('='*60)
    cmd = "gitleaks detect --source . --verbose --no-color"
    result = subprocess.run(cmd, shell=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        print("ALERTA: Gitleaks detecto secretos o patrones sospechosos")
        return False
    print("OK: No se detectaron secretos")
    return True


def check_env_not_committed():
    print(f"\n{'='*60}")
    print("  4. Verificando que .env no este en git")
    print('='*60)
    cmd = 'git ls-files --error-unmatch .env 2>nul'
    result = subprocess.run(cmd, shell=True, cwd=REPO_ROOT)
    if result.returncode == 0:
        print("CRITICO: .env esta commiteado en git!")
        return False
    print("OK: .env no esta en git")
    return True


def check_gitignore_has_env():
    print(f"\n{'='*60}")
    print("  5. Verificando .env en .gitignore")
    print('='*60)
    gitignore = REPO_ROOT / ".gitignore"
    if not gitignore.exists():
        print("WARNING: No existe .gitignore")
        return False
    content = gitignore.read_text()
    if ".env" not in content:
        print("CRITICO: .env no esta en .gitignore!")
        return False
    print("OK: .env en .gitignore")
    return True


def check_precommit_config():
    print(f"\n{'='*60}")
    print("  6. Verificando .pre-commit-config.yaml")
    print('='*60)
    pc = REPO_ROOT / ".pre-commit-config.yaml"
    if not pc.exists():
        print("CRITICO: No existe .pre-commit-config.yaml")
        return False
    print("OK: .pre-commit-config.yaml existe")
    return True


def run_precommit():
    print(f"\n{'='*60}")
    print("  7. Ejecutando pre-commit (todos los hooks)")
    print('='*60)
    print("Esto puede tomar unos segundos...")
    cmd = "pre-commit run --all-files"
    result = subprocess.run(cmd, shell=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        print("ALERTA: Pre-commit detecto issues")
        return False
    print("OK: Todos los hooks pasaron")
    return True


def main():
    print("="*60)
    print("  CUSTODIO RAT - Security Audit Local")
    print("="*60)
    print(f"Repo: {REPO_ROOT}")

    checks = [
        ("Pre-commit instalado", check_precommit_installed),
        ("Gitleaks instalado", check_gitleaks),
        (".env no commiteado", check_env_not_committed),
        (".env en .gitignore", check_gitignore_has_env),
        (".pre-commit-config.yaml existe", check_precommit_config),
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
        status = "OK" if ok else "FALLA"
        print(f"  [{status}] {name}")
        if not ok:
            all_ok = False

    print("\n" + "="*60)
    if all_ok:
        print("  SECURITY AUDIT: PASSED")
        print("="*60)
        return 0
    else:
        print("  SECURITY AUDIT: FAILED - Corregir los items marcados")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
