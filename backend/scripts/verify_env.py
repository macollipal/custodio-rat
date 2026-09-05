"""Verifica que el .env local tiene todos los secrets necesarios
y NO contiene passwords viejos o comprometidos.

Uso:
    python backend/scripts/verify_env.py

Exit codes:
    0 = OK
    1 = Error (falta variable o contiene secret viejo)
"""
import os
import re
import sys
from pathlib import Path


# Passwords viejos que ya fueron comprometidos (NO USAR)
COMPROMISED_PASSWORDS = {
    'npg_9GlXps5ztVRy': 'custodio_test (script check_*.py)',
    'npg_RVH63hjIvwAD': 'custodio_test (scripts check_*.py)',
    'npg_AucohCmFHI31': 'config.py (viejo)',
    'npg_Rem3X0tGwUxv': '.env (Custodio_dev - linea comentada)',
}

# Variables requeridas
REQUIRED_VARS = {
    'DATABASE_URL': 'URL de BD principal (neondb)',
    'TEST_DATABASE_URL': 'URL de BD test (custodio_test)',
    'SECRET_KEY': 'Secret para JWT (64 hex chars)',
    'ALLOWED_ORIGINS': 'Lista blanca de origenes CORS',
}

# Patterns de secrets que NUNCA deben estar
FORBIDDEN_PATTERNS = [
    (r'password\s*[:=]\s*["\'][^"\']{8,}["\']', 'password hardcodeado'),
    (r'sk-[A-Za-z0-9]{20,}', 'OpenAI API key'),
    (r'AKIA[A-Z0-9]{16}', 'AWS access key'),
]


def main():
    print('Verificando .env local...\n')

    # Cargar .env
    env_path = Path(__file__).parent.parent / '.env'
    if not env_path.exists():
        print(f'[FAIL] {env_path} no existe')
        print('  Solucion: cp backend/.env.example backend/.env')
        return 1

    env_content = env_path.read_text(encoding='utf-8')
    env_vars = {}
    for line in env_content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            k, v = line.split('=', 1)
            env_vars[k.strip()] = v.strip()

    # 1. Verificar variables requeridas
    missing = []
    for var, desc in REQUIRED_VARS.items():
        if var not in env_vars or not env_vars[var]:
            missing.append(f'{var} ({desc})')

    if missing:
        print('[FAIL] Variables faltantes:')
        for m in missing:
            print(f'  - {m}')
        return 1
    print('[OK] Todas las variables requeridas presentes')

    # 2. Verificar placeholders en .env.example
    example_path = Path(__file__).parent.parent / '.env.example'
    if example_path.exists():
        example_content = example_path.read_text(encoding='utf-8')
        if '<TU_' in example_content:
            print('[OK] .env.example tiene placeholders')
        else:
            print('[WARN] .env.example NO tiene placeholders <TU_*>')

    # 3. Verificar que .env NO contiene passwords viejos
    compromised_found = []
    for old_pwd, location in COMPROMISED_PASSWORDS.items():
        # Buscar como substring
        if old_pwd in env_content:
            compromised_found.append((old_pwd, location))

    if compromised_found:
        print('\n[CRITICAL] Passwords viejos detectados en .env:')
        for pwd, loc in compromised_found:
            print(f'  - {pwd[:8]}... ({loc})')
        print('\n  Accion: ROTAR INMEDIATAMENTE y actualizar .env')
        return 1
    print('[OK] Sin passwords viejos en .env')

    # 4. Verificar que DATABASE_URL es una URL valida
    db_url = env_vars.get('DATABASE_URL', '')
    if not db_url.startswith('postgresql://'):
        print(f'[FAIL] DATABASE_URL no es una URL PostgreSQL valida: {db_url[:30]}...')
        return 1
    print('[OK] DATABASE_URL es PostgreSQL valida')

    # 5. Verificar que SECRET_KEY tiene largo suficiente
    secret_key = env_vars.get('SECRET_KEY', '')
    if len(secret_key) < 32:
        print(f'[WARN] SECRET_KEY muy corto ({len(secret_key)} chars). Recomendado >= 64')

    # 6. Verificar patterns prohibidos en .env
    for pattern, desc in FORBIDDEN_PATTERNS:
        matches = re.findall(pattern, env_content, re.IGNORECASE)
        if matches:
            print(f'[FAIL] {desc} detectado en .env: {matches[0][:20]}...')
            return 1

    print('\n[OK] .env verificado correctamente')
    return 0


if __name__ == '__main__':
    sys.exit(main())