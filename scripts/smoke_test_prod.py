"""
Smoke test post-deploy para Custodio RAT Manager.

Uso:
    python smoke_test_prod.py --env prod

Valida que:
- Backend health endpoint responde 200
- Database esta conectada
- Frontend carga HTML
- CORS permite requests del frontend
- Login funciona con credenciales de prueba
- Bundle JS del frontend NO contiene 'localhost' (evidencia que env vars se aplicaron)

Exit codes:
    0 = todo OK
    1 = fallo critico
    2 = warning
"""

import requests
import sys
import re
import json
import argparse
from typing import Tuple, List

# Configuracion por ambiente
CONFIGS = {
    'qa': {
        'frontend': 'https://custodio-qa.vercel.app',
        'backend': 'https://custodio-qa.vercel.app',
        'test_user': 'admin',
        'test_password': 'admin',  # Usuario por defecto en QA
    },
    'prod': {
        'frontend': 'https://custodio-prod.vercel.app',
        'backend': 'https://custodio-api-prod.vercel.app',
        'test_user': 'claudio_admin',
        'test_password': 'Claudio2026!',
    },
    'local': {
        'frontend': 'http://localhost:3000',
        'backend': 'http://localhost:8002',
        'test_user': None,
        'test_password': None,
    }
}

def check(name: str, ok: bool, detail: str = '') -> bool:
    icon = '[OK]' if ok else '[FAIL]'
    print(f'  {icon} {name}: {detail}')
    return ok

def check_warn(name: str, ok: bool, detail: str = '') -> bool:
    icon = '[OK]' if ok else '[WARN]'
    print(f'  {icon} {name}: {detail}')
    return ok

def run_smoke_test(env: str) -> int:
    if env not in CONFIGS:
        print(f'[ERROR] Ambiente invalido: {env}. Opciones: {", ".join(CONFIGS.keys())}')
        return 1

    cfg = CONFIGS[env]
    print(f'=' * 60)
    print(f'SMOKE TEST - Ambiente: {env.upper()}')
    print(f'=' * 60)
    print(f'Frontend: {cfg["frontend"]}')
    print(f'Backend:  {cfg["backend"]}')
    print()

    failures = []
    warnings = []

    # 1. Health check
    print('[1] HEALTH CHECKS')
    try:
        r = requests.get(f'{cfg["backend"]}/health', timeout=10)
        if not check('Backend /health', r.status_code == 200, f'status={r.status_code} body={r.text[:60]}'):
            failures.append('Backend health')
    except Exception as e:
        check('Backend /health', False, str(e))
        failures.append('Backend health unreachable')

    try:
        r = requests.get(f'{cfg["backend"]}/health/db', timeout=10)
        ok = r.status_code == 200 and r.json().get('status') == 'ok'
        if not check('Backend /health/db', ok, f'status={r.status_code} body={r.text[:80]}'):
            failures.append('Backend DB connection')
    except Exception as e:
        check('Backend /health/db', False, str(e))
        failures.append('Backend DB unreachable')

    # 2. Frontend carga
    print()
    print('[2] FRONTEND')
    js_files = []
    try:
        r = requests.get(cfg['frontend'], timeout=10, allow_redirects=True)
        if check('Frontend accesible', r.status_code == 200, f'status={r.status_code}'):
            html = r.text
            # Buscar archivos JS
            js_matches = re.findall(r'_next/static/chunks/[^"]+\.js', html)
            js_files = list(set(js_matches))
            check_warn('JS bundles encontrados', len(js_files) > 0, f'{len(js_files)} archivos')
        else:
            failures.append('Frontend no carga')
    except Exception as e:
        check('Frontend accesible', False, str(e))
        failures.append('Frontend unreachable')

    # 3. Verificar que bundle JS NO contiene localhost (CRITICO)
    print()
    print('[3] VERIFICACION DE ENV VARS EN BUNDLE (CRITICO)')
    localhost_count = 0
    backend_url_count = 0
    for js_file in js_files[:5]:  # Solo los primeros 5
        try:
            js_url = f'{cfg["frontend"]}/{js_file}'
            r = requests.get(js_url, timeout=10)
            if 'localhost' in r.text.lower():
                localhost_count += 1
            if cfg['backend'].split('//')[1] in r.text:
                backend_url_count += 1
        except Exception:
            pass

    check('Bundle NO contiene localhost:8002', localhost_count == 0,
          f'{localhost_count}/{min(5, len(js_files))} bundles con localhost')
    if localhost_count > 0:
        failures.append('Bundle JS contiene localhost (env vars NO aplicadas)')

    check_warn(f'Bundle contiene URL del backend ({cfg["backend"]})', backend_url_count > 0,
               f'{backend_url_count}/{min(5, len(js_files))} bundles')

    # 4. CORS
    print()
    print('[4] CORS')
    try:
        r = requests.get(f'{cfg["backend"]}/health', timeout=10,
                         headers={'Origin': cfg['frontend']})
        cors_origin = r.headers.get('Access-Control-Allow-Origin', '')
        ok = cors_origin == cfg['frontend'] or cors_origin == '*'
        check(f'CORS permite {cfg["frontend"]}', ok, f'Access-Control-Allow-Origin={cors_origin}')
        if not ok:
            failures.append('CORS mal configurado')
    except Exception as e:
        check('CORS test', False, str(e))

    # 5. Login funcional
    print()
    print('[5] LOGIN FUNCIONAL')
    if cfg.get('test_user'):
        try:
            r = requests.post(f'{cfg["backend"]}/auth/login', timeout=10,
                              json={'username': cfg['test_user'], 'password': cfg['test_password']},
                              headers={'Origin': cfg['frontend']})
            if check(f'Login {cfg["test_user"]}', r.status_code == 200, f'status={r.status_code}'):
                data = r.json()
                check('Token recibido', 'access_token' in data, f'keys={list(data.keys())[:5]}')
                check('User data recibido', 'user' in data, f'rol={data.get("user", {}).get("rol_global")}')

                # Test endpoint protegido
                token = data['access_token']
                r2 = requests.get(f'{cfg["backend"]}/auth/me', timeout=10,
                                  headers={'Authorization': f'Bearer {token}'})
                check('Endpoint protegido /auth/me', r2.status_code == 200, f'status={r2.status_code}')
            else:
                failures.append(f'Login fallo: {r.text[:100]}')
        except Exception as e:
            check('Login', False, str(e))
            failures.append('Login exception')
    else:
        check_warn('Login', True, 'skip (no test_user configurado)')

    # Resumen
    print()
    print('=' * 60)
    if failures:
        print(f'[FAIL] {len(failures)} fallos criticos:')
        for f in failures:
            print(f'  - {f}')
        return 1
    else:
        print('[OK] Todos los smoke tests pasaron')
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Smoke test post-deploy')
    parser.add_argument('--env', required=True, choices=['qa', 'prod', 'local'],
                        help='Ambiente a testear')
    args = parser.parse_args()

    sys.exit(run_smoke_test(args.env))