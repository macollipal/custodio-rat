"""
build_all.py - Regenera los 9 .docx del modulo Asesor en _regen/.
Uso:
    cd paso\desarrollo_de_software_estandar\_build\asesor
    python build_all.py
"""
import os
import subprocess
import sys

THIS = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = [
    "build_01_vision_alcance_asesorgpt_v1_0.py",
    "build_02_requisitos_hu_asesorgpt_v1_0.py",
    "build_03_cu_diseno_asesorgpt_v1_0.py",
    "build_04_arquitectura_datos_asesorgpt_v1_0.py",
    "build_05_api_backlog_asesorgpt_v1_0.py",
    "build_06_qa_asesorgpt_v1_0.py",
    "build_07_despliegue_tecnico_asesorgpt_v1_0.py",
    "build_08_modulo_asesor_asesorgpt_v1_0.py",
    "build_matriz_asesorgpt_v1_0.py",
]

PYTHON = r"C:\Users\chelo\Desktop\RAT_opencode\backend\venv\Scripts\python.exe"

for s in SCRIPTS:
    path = os.path.join(THIS, s)
    print(f"\n[RUN] {s}")
    result = subprocess.run([PYTHON, path], capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print(f"  [ERROR] returncode={result.returncode}")
        print(result.stderr[:500])

print("\n[OK] Build completo. Output en docs/documentacion_oficial_asesorgpt/_regen/")
