"""
Validacion de env vars requeridas antes de hacer build/deploy.

Uso:
    python validate_env.py --env prod
    python validate_env.py --env qa
    python validate_env.py --env local

Exit codes:
    0 = todas las env vars presentes
    1 = faltan env vars (bloquea el deploy)
"""

import os
import sys
import argparse
from pathlib import Path

REQUIRED_VARS = {
    'local': {
        'frontend': {
            'NEXT_PUBLIC_API_BASE': 'http://localhost:8002',
            'NEXT_PUBLIC_DEPLOY_ENV': 'local',
        },
        'backend': {
            'SECRET_KEY': '<any-non-empty>',
            'ENVIRONMENT': 'development',
        }
    },
    'qa': {
        'frontend': {
            'NEXT_PUBLIC_API_BASE': 'https://custodio-qa.vercel.app',
            'NEXT_PUBLIC_DEPLOY_ENV': 'qa',
        },
        'backend': {
            'SECRET_KEY': '<required>',
            'ENVIRONMENT': 'qa',
            'ALLOWED_ORIGINS': 'https://custodio-qa.vercel.app,http://localhost:3000',
        }
    },
    'prod': {
        'frontend': {
            'NEXT_PUBLIC_API_BASE': 'https://custodio-api-prod.vercel.app',
            'NEXT_PUBLIC_DEPLOY_ENV': 'production',
        },
        'backend': {
            'SECRET_KEY': '<required>',
            'ENVIRONMENT': 'production',
            'ALLOWED_ORIGINS': 'https://custodio-prod.vercel.app',
        }
    }
}

def load_env_file(env_file: Path) -> dict:
    """Lee un archivo .env y devuelve dict de variables"""
    env_vars = {}
    if not env_file.exists():
        return env_vars
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            env_vars[key.strip()] = value.strip()
    return env_vars

def validate_env(env: str, target: str = 'all') -> int:
    if env not in REQUIRED_VARS:
        print(f'[ERROR] Ambiente invalido: {env}')
        return 1

    required = REQUIRED_VARS[env]
    base_dir = Path(__file__).resolve().parent.parent
    failures = []

    print('=' * 60)
    print(f'VALIDACION DE ENV VARS - Ambiente: {env.upper()}')
    print('=' * 60)

    targets_to_check = []
    if target == 'all':
        targets_to_check = ['frontend', 'backend']
    else:
        targets_to_check = [target]

    for t in targets_to_check:
        if t not in required:
            continue

        print(f'\n[{t.upper()}]')

        # Leer .env file
        if t == 'frontend':
            env_file = base_dir / 'frontend-next' / '.env.local'
        else:
            env_file = base_dir / 'backend' / '.env'

        env_vars_from_file = load_env_file(env_file)
        if env_vars_from_file:
            print(f'  [INFO] Leyendo de: {env_file.relative_to(base_dir)}')
        else:
            print(f'  [WARN] Archivo {env_file.name} no existe o vacio')

        # Verificar cada variable requerida
        for var, expected in required[t].items():
            # Buscar primero en process.env (Vercel), luego en .env file
            actual = os.environ.get(var) or env_vars_from_file.get(var, '')

            # Validar
            if not actual:
                print(f'  [FAIL] {var} - NO CONFIGURADA (esperado: {expected})')
                failures.append(f'{t}.{var}')
            elif expected.startswith('<') and expected.endswith('>'):
                # Placeholder - solo verificar que no este vacia
                print(f'  [OK] {var} - configurada (valor: {actual[:8]}...)')
            else:
                # Verificar que coincida con el valor esperado
                if actual == expected:
                    print(f'  [OK] {var} = {actual}')
                else:
                    print(f'  [WARN] {var} = {actual} (esperado: {expected})')

    # Resumen
    print('\n' + '=' * 60)
    if failures:
        print(f'[FAIL] {len(failures)} variables faltantes:')
        for f in failures:
            print(f'  - {f}')
        print()
        print('ACCION REQUERIDA:')
        print('  - Local: Agregar a frontend-next/.env.local o backend/.env')
        print('  - Vercel: Configurar en Settings > Environment Variables')
        return 1
    else:
        print('[OK] Todas las env vars requeridas estan configuradas')
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validar env vars antes de build')
    parser.add_argument('--env', required=True, choices=['qa', 'prod', 'local'],
                        help='Ambiente a validar')
    parser.add_argument('--target', default='all', choices=['frontend', 'backend', 'all'],
                        help='Que app validar')
    args = parser.parse_args()

    sys.exit(validate_env(args.env, args.target))