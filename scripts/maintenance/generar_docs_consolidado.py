"""
generar_docs_consolidado.py
============================
Genera documentos Word v1.13 COMPLETAMENTE ACUMULATIVOS desde v1.0.

Estrategia:
  1. Ejecuta los scripts v1.10 (base acumulativa más completa disponible)
     en su propio directorio para que importen _theme_custodio correctamente.
  2. Abre cada .docx resultante con python-docx.
  3. Inserta secciones con el contenido incremental de v1.11 y v1.12.
  4. Guarda como v1.13 en docs/documentacion_oficial/.
  5. Elimina los archivos intermedios v1.10 para no dejar duplicados.

Documentos generados:
  02_Requisitos, 03_Historias_Usuario, 09_Backlog_Producto, 10_Plan_QA
  (04, 06, 08, 12, MTX se actualizan por separado cuando se disponga
   de sus scripts acumulativos v1.10)
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ── Rutas ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent.parent   # RAT_opencode/
OUT_DIR = ROOT / "docs" / "documentacion_oficial"
AUD_V110 = ROOT / "docs" / "auditorias" / "2026-07-18_auditoria_doc_v1.10" / "_scripts"
AUD_V17  = ROOT / "docs" / "auditorias" / "2026-06-24_auditoria_v1.7" / "_scripts"
AUD_V111 = ROOT / "docs" / "auditorias" / "2026-08-22_auditoria_qa_tests" / "_scripts"

VERSION = "v1.13"
COLOR_PRI = RGBColor(0x1F, 0x49, 0x7D)   # azul Custodio

# ── Utilidades python-docx ────────────────────────────────────────────────────

def _shading(cell, fill_hex="1F497D"):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill_hex)
    tcPr.append(shd)


def add_table(doc, headers, rows, col_widths_cm=None, shade_header=True):
    """Tabla con cabecera sombreada."""
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    # cabecera
    hrow = t.rows[0]
    for i, h in enumerate(headers):
        cell = hrow.cells[i]
        cell.text = h
        for para in cell.paragraphs:
            for run in para.runs:
                run.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                run.font.size = Pt(9)
        if shade_header:
            _shading(cell)
    # filas
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            cell = t.rows[r + 1].cells[c]
            cell.text = str(val)
            for para in cell.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(9)
    # anchos opcionales
    if col_widths_cm:
        for r_idx, row in enumerate(t.rows):
            for c_idx, cell in enumerate(row.cells):
                if c_idx < len(col_widths_cm):
                    cell.width = Cm(col_widths_cm[c_idx])
    return t


def add_italic_note(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(10)


def section_heading(doc, text, level=1):
    doc.add_heading(text, level=level)

# ── Runner de script v1.10 ────────────────────────────────────────────────────

def run_script(script_path: Path) -> bool:
    """Ejecuta un script build en su propio directorio."""
    print(f"  → {script_path.name}...")
    res = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(script_path.parent),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if res.returncode != 0:
        print(f"    ERROR: {res.stderr[-400:]}")
        return False
    print(f"    OK: {(res.stdout or '').strip()[-120:]}")
    return True


def find_docx(prefix: str):
    hits = sorted(OUT_DIR.glob(f"{prefix}*.docx"), key=lambda p: p.stat().st_mtime, reverse=True)
    return hits[0] if hits else None


def rename_to_v113(path: Path) -> Path:
    """Renombra un .docx quitando su versión e insertando v1.13."""
    stem = path.stem
    # Quita _v1.xx al final si existe
    import re
    stem_clean = re.sub(r"_v\d+\.\d+$", "", stem)
    new_name = OUT_DIR / f"{stem_clean}_{VERSION}.docx"
    return new_name


# ══════════════════════════════════════════════════════════════════════════════
# 02 — Requisitos
# ══════════════════════════════════════════════════════════════════════════════

def consolidar_02_requisitos():
    print("\n[02] Requisitos...")

    # 1. Base acumulativa v1.10 (RF-001 a RF-169 + todas las RNF)
    ok = run_script(AUD_V110 / "build_02_requisitos_v1_10.py")
    if not ok:
        return

    base = find_docx("02_Requisitos")
    if not base:
        print("  WARN: no se encontró 02_Requisitos*.docx")
        return

    doc = Document(str(base))

    # 2. Nuevos en v1.12 — RF-174 a RF-179
    section_heading(doc, "Requisitos Funcionales v1.12 (Septiembre 2026)", level=1)
    doc.add_paragraph(
        "Los siguientes requisitos funcionales fueron añadidos en la iteración v1.12:"
    )
    rf_v112 = [
        ["RF-174", "Alta", "ARCO público", "GET /publico/verificar-titular: banner amarillo si el email ya tiene un TKT abierto (Art. 12)."],
        ["RF-175", "Alta", "ARCO público", "POST /tkt-solicitud-derecho/: acuse de recibo automático al titular con código de seguimiento y plazo (email en ≤5 min)."],
        ["RF-176", "Media", "ARCO interno", "TicketDrawer.tsx: chips de placeholders dinámicos bajo el textarea de respuesta para agilizar redacción."],
        ["RF-177", "Alta", "ARCO interno", "FlujoModal.tsx: semáforo SLA visual (verde/amarillo/rojo) con días hábiles transcurridos y restantes."],
        ["RF-178", "Alta", "Empresas", "CompanyFichaPanel.tsx: ficha completa de empresa con 4 tabs lazy (RATs, ARCO, Brechas, Stats) — Art. 16 Ley 21.719."],
        ["RF-179", "Alta", "DevSecOps", "CI/CD pip-audit: cero vulnerabilidades críticas en dependencias Python antes de cada deploy."],
    ]
    add_table(doc, ["RF", "Prioridad", "Módulo", "Descripción"], rf_v112,
              col_widths_cm=[1.5, 1.5, 2.5, 12.0])

    # 3. Nuevos en v1.12 — RNF-21, RNF-22
    section_heading(doc, "Requisitos No Funcionales v1.12", level=2)
    rnf_v112 = [
        ["RNF-21", "Global (código, tests, docs)", "Nomenclatura APDP: usar 'titular' en lugar de 'solicitante' en toda la aplicación (art. 12 Ley 21.719)."],
        ["RNF-22", "GET /publico/verificar-titular", "Rate-limit: máximo 10 peticiones por hora por IP para prevenir abuso de la búsqueda por email."],
    ]
    add_table(doc, ["RNF", "Alcance", "Descripción"], rnf_v112,
              col_widths_cm=[1.5, 4.0, 12.0])

    # 4. Guardar como v1.13
    dest = rename_to_v113(base)
    # Eliminar v1.13 anterior si existe
    if dest.exists():
        dest.unlink()
    doc.save(str(dest))
    # Limpiar intermedio v1.10 si es diferente al destino
    if base != dest and base.exists():
        base.unlink()
    print(f"  ✓ {dest.name}")


# ══════════════════════════════════════════════════════════════════════════════
# 03 — Historias de Usuario
# ══════════════════════════════════════════════════════════════════════════════

def consolidar_03_historias():
    print("\n[03] Historias de Usuario...")

    # 1. Base acumulativa: v1.7 tiene HU-001 a HU-085 (mejor base cumplativa)
    ok = run_script(AUD_V17 / "build_03_historias_usuario_v1_7.py")
    if not ok:
        return

    base = find_docx("03_Historias")
    if not base:
        print("  WARN: no se encontró 03_Historias*.docx")
        return

    doc = Document(str(base))

    # 2. HU-064 a HU-071 (v1.5 Seguridad + v1.6 UI/UX — ausentes en tabla v1.7)
    section_heading(doc, "HU-064 a HU-071 — Seguridad y UI/UX (v1.5 y v1.6)", level=1)
    add_italic_note(doc,
        "Estas HUs corresponden a las iteraciones v1.5 (Seguridad) y v1.6 (UI/UX). "
        "Completan el listado entre HU-063 y HU-072."
    )
    hus_v15_v16 = [
        ["HU-064", "EP-01", "RNF-114", "Alta", "M",  "Implementar CSRF middleware en todos los endpoints públicos (Art. seguridad)"],
        ["HU-065", "EP-01", "RNF-115", "Alta", "L",  "Encryption at Rest: cifrado Fernet para datos sensibles en BD (BYTEA)"],
        ["HU-066", "EP-02", "RNF-116", "Alta", "M",  "Service Layer: extraer lógica de negocio de routes a services/"],
        ["HU-067", "EP-02", "RNF-040", "Media", "S", "Schemas Pydantic v2: separar Request/Response en schemas independientes"],
        ["HU-068", "EP-02", "RF-029",  "Alta", "M",  "RatDetailModal: modal de detalle RAT con vista completa de 25 campos"],
        ["HU-069", "EP-05", "RF-064",  "Alta", "S",  "Drawer ARCO responsive: diseño adaptado a móvil con breakpoints Tailwind"],
        ["HU-070", "EP-06", "RF-074",  "Media", "S", "Dashboard clickable: cards del dashboard navegan a filtros pre-aplicados"],
        ["HU-071", "EP-02", "RF-027",  "Baja", "S",  "Sort estable en tablas: mantiene orden secundario al reordenar columnas"],
    ]
    add_table(doc, ["HU", "Épica", "Trazabilidad RF/RNF", "Prioridad", "Tamaño", "Título"],
              hus_v15_v16, col_widths_cm=[1.3, 1.3, 2.0, 1.4, 1.2, 10.3])

    # 3. HU-086 a HU-103 (v1.10 — Iter 11+12 y fixes v1.9)
    section_heading(doc, "HU-086 a HU-103 — Iter 11+12 y Fixes (v1.10)", level=1)
    hus_v110 = [
        # Iter 11: 15 campos Tier 1+2
        ["HU-086", "EP-02", "RF-141",      "Alta",   "M", "Registrar datos NNA en RAT (datos_nna, datos_anonimizados, datos_seudonimizados)"],
        ["HU-087", "EP-02", "RF-142–149",  "Media",  "S", "Registrar nivel de confidencialidad y estructura del dato"],
        ["HU-088", "EP-02", "RF-146–149",  "Media",  "S", "Registrar ciclo de procesamiento y frecuencia de tratamiento"],
        ["HU-089", "EP-02", "RF-150–155",  "Media",  "M", "Registrar campos operativos Tier 2 (sistema_almacenamiento, volumen, email, etc.)"],
        # Iter 12: fixes críticos
        ["HU-090", "EP-02", "RF-156",      "CRÍTICO","S", "Validar límite 10 MB en archivos BYTEA (archivo_base_legal, tkt_adjunto)"],
        ["HU-091", "EP-02", "RF-157",      "CRÍTICO","S", "Test de interés legítimo con mínimo 50 caracteres (Art. 16 Ley 21.719)"],
        ["HU-092", "EP-05", "RF-158",      "CRÍTICO","M", "Hash SHA-256 de evidencia ARCO computado automáticamente al resolver TKT"],
        ["HU-093", "EP-05", "RF-159",      "ALTO",   "S", "causal_rechazo con enum cerrado de 7 causales Art. 29 RL"],
        ["HU-094", "EP-05", "RF-160",      "ALTO",   "S", "Toggle ARCO con touch target 44×44px para accesibilidad móvil (WCAG 2.1)"],
        ["HU-095", "EP-04", "RF-161",      "ALTO",   "M", "Notificación APDC automatizada al marcar notificado_apdc=true en brecha"],
        ["HU-096", "EP-04", "RF-162",      "ALTO",   "M", "Notificación a titulares automatizada al marcar notificado_titulares=true"],
        ["HU-097", "EP-05", "RF-158",      "ALTO",   "S", "TKT no puede resolverse sin evidencia ni hash SHA-256 (HTTP 400)"],
        # v1.10 fixes (Julio 2026)
        ["HU-098", "EP-02", "RF-163",      "CRÍTICO","M", "IDOR multi-tenant: get_rat_for_user() retorna 404 si empresa no coincide; superadmin accede a todos"],
        ["HU-099", "EP-02", "RF-164",      "ALTO",   "S", "base_legal_valida strict: validación contra enum taxativo de 6 opciones"],
        ["HU-100", "EP-11", "RF-165",      "ALTO",   "S", "ConsentimientoAlert: listarConsentimientos() antes de guardar si datos_sensibles=True"],
        ["HU-101", "EP-02", "RF-166",      "ALTO",   "L", "Homologación orden campos RAT entre RatDetailView, RatEditForm, RatWizard y PDF (5 pasos canónicos)"],
        ["HU-102", "EP-06", "RF-167",      "MEDIO",  "M", "PDF con títulos de sección (PASO 1 — IDENTIFICACIÓN, etc.) con fondo COLOR_PRIMARIO"],
        ["HU-103", "EP-02", "RF-168",      "MEDIO",  "S", "Encoding UTF-8 corregido en backend: ALERTAS_AUDITORIA, regex, conftest.py, main.py"],
    ]
    add_table(doc, ["HU", "Épica", "Trazabilidad", "Prioridad", "Tamaño", "Título"],
              hus_v110, col_widths_cm=[1.3, 1.3, 2.0, 1.4, 1.2, 10.3])

    # 4. HU-104 a HU-108 (v1.12)
    section_heading(doc, "HU-104 a HU-108 — ARCO y Empresa (v1.12)", level=1)
    hus_v112 = [
        ["HU-104", "EP-05", "RF-174", "Alta",  "S", "Titular: detección de solicitud ARCO duplicada antes de enviar (banner amarillo)"],
        ["HU-105", "EP-05", "RF-175", "Alta",  "S", "Titular: acuse de recibo inmediato con código de seguimiento y plazo (email ≤5 min)"],
        ["HU-106", "EP-05", "RF-176", "Media", "S", "Operador DPO: insertar placeholders dinámicos en respuesta al titular con un clic"],
        ["HU-107", "EP-05", "RF-177", "Alta",  "S", "Operador DPO: semáforo SLA visual verde/amarillo/rojo con días hábiles transcurridos"],
        ["HU-108", "EP-01", "RF-178", "Alta",  "M", "Admin empresa: ficha completa con 4 tabs lazy (RATs, ARCO, Brechas, Stats)"],
    ]
    add_table(doc, ["HU", "Épica", "Trazabilidad", "Prioridad", "Tamaño", "Título"],
              hus_v112, col_widths_cm=[1.3, 1.3, 2.0, 1.4, 1.2, 10.3])

    # 5. Guardar como v1.13
    dest = rename_to_v113(base)
    if dest.exists():
        dest.unlink()
    doc.save(str(dest))
    if base != dest and base.exists():
        base.unlink()
    print(f"  ✓ {dest.name}")


# ══════════════════════════════════════════════════════════════════════════════
# 09 — Backlog de Producto
# ══════════════════════════════════════════════════════════════════════════════

def consolidar_09_backlog():
    print("\n[09] Backlog de Producto...")

    # 1. Base acumulativa v1.10 (items v1.0 a v1.9)
    ok = run_script(AUD_V110 / "build_09_backlog_v1_10.py")
    if not ok:
        return

    base = find_docx("09_Backlog")
    if not base:
        print("  WARN: no se encontró 09_Backlog*.docx")
        return

    doc = Document(str(base))

    # 2. Items nuevos v1.12 (cerrados + pendientes actualizados)
    section_heading(doc, "Items Cerrados en v1.12 (Septiembre 2026)", level=1)
    items_v112_cerrados = [
        ["TKT-V112-01", "P1", "Feature", "Detección duplicado ARCO: GET /publico/verificar-titular — RF-174", "CERRADO"],
        ["TKT-V112-02", "P1", "Feature", "Acuse de recibo automático al titular: email en ≤5 min — RF-175", "CERRADO"],
        ["TKT-V112-03", "P2", "Feature", "Chips placeholders en TicketDrawer.tsx — RF-176", "CERRADO"],
        ["TKT-V112-04", "P1", "Feature", "Semáforo SLA en FlujoModal.tsx — RF-177", "CERRADO"],
        ["TKT-V112-05", "P1", "Feature", "Ficha empresa con 4 tabs lazy (CompanyFichaPanel.tsx) — RF-178", "CERRADO"],
        ["TKT-V112-06", "P1", "DevSecOps", "pip-audit en CI/CD: 0 vulns críticas Python — RF-179", "CERRADO"],
        ["TKT-V112-07", "P2", "Nomenclatura", "Renombrar 'solicitante' → 'titular' en toda la app — RNF-21", "CERRADO"],
        ["TKT-V112-08", "P2", "Seguridad", "Rate-limit en GET /publico/verificar-titular — RNF-22", "CERRADO"],
    ]
    add_table(doc, ["ID", "Prioridad", "Tipo", "Título", "Estado"],
              items_v112_cerrados, col_widths_cm=[2.2, 1.5, 2.0, 10.5, 1.7])

    section_heading(doc, "Items Pendientes Actualizados (v1.12)", level=1)
    items_pendientes = [
        ["QW-ITER14-01", "P2", "Feature", "Paginación en listados >100 registros (RAT/ARCO/Brechas/Encargados)"],
        ["QW-ITER14-02", "P3", "Feature", "Retry logic en OCI uploads (resiliencia ante timeouts)"],
        ["QW-ITER14-03", "P2", "Feature", "Logs de auditoría en tabla audit_log independiente (Art. 28 Ley 21.719)"],
        ["QW-ITER14-04", "P3", "Feature", "ALTER TABLE categoria_titulares SET NOT NULL (requiere migración coordinada)"],
    ]
    add_table(doc, ["ID", "Prioridad", "Tipo", "Título"],
              items_pendientes, col_widths_cm=[2.2, 1.5, 2.0, 12.2])

    dest = rename_to_v113(base)
    if dest.exists():
        dest.unlink()
    doc.save(str(dest))
    if base != dest and base.exists():
        base.unlink()
    print(f"  ✓ {dest.name}")


# ══════════════════════════════════════════════════════════════════════════════
# 10 — Plan de QA
# ══════════════════════════════════════════════════════════════════════════════

def consolidar_10_plan_qa():
    print("\n[10] Plan de QA...")

    # 1. Base v1.10 (TC-030 a TC-046 — previos en documento v1.9 ya embebidos)
    ok = run_script(AUD_V110 / "build_10_plan_qa_v1_10.py")
    if not ok:
        return

    base = find_docx("10_Plan_QA")
    if not base:
        print("  WARN: no se encontró 10_Plan_QA*.docx")
        return

    doc = Document(str(base))

    # 2. TC-047 a TC-055 (v1.11 — QA Total 2026-08-22)
    section_heading(doc, "Casos de Prueba v1.11 — QA Total (22 Ago 2026)", level=1)
    add_italic_note(doc, "v1.11: QA Total completado. 78 fallos → 0. Suite final: 732 tests, 0 fallos.")
    tc_v111 = [
        ["TC-047", "CRÍTICO", "Backend",  "PATCH TKT resuelto CON metodo_verificacion_identidad → 200",
         "PATCH /tkt-solicitud-derecho/{id} con estado=resuelto + metodo_verificacion_identidad",
         "HTTP 200, estado=resuelto", "pytest"],
        ["TC-048", "CRÍTICO", "Backend",  "Prorrogar TKT desde estado resuelto → 400",
         "POST /tkt-solicitud-derecho/{id}/prorrogar (ticket resuelto)",
         "HTTP 400", "pytest"],
        ["TC-049", "ALTO",    "Backend",  "POST /auth/users retorna 201 al crear usuario nuevo",
         "POST /auth/users con datos válidos",
         "HTTP 201 con objeto usuario", "pytest"],
        ["TC-050", "ALTO",    "Backend",  "encrypt_existing_bytea falla si ENCRYPTION_KEY='' (sin fallback)",
         "Ejecutar _check_prerequisites() con ENCRYPTION_KEY=''",
         "SystemExit", "pytest"],
        ["TC-051", "ALTO",    "Backend",  "encrypt_existing_bytea detecta datos ya cifrados como Fernet",
         "is_already_encrypted(fernet.encrypt(b'test'))",
         "True", "pytest"],
        ["TC-052", "ALTO",    "Backend",  "encrypt_existing_bytea dry-run no modifica BD",
         "_migrate_table(..., dry_run=True)",
         "stats['migrados']==0, datos sin cambios", "pytest"],
        ["TC-053", "ALTO",    "Backend",  "encrypt_existing_bytea segunda pasada idempotente",
         "_migrate_table() dos veces sobre mismos datos",
         "Segunda: ya_cifrados=1, migrados=0", "pytest"],
        ["TC-054", "ALTO",    "Backend",  "EIPD validator bloquea datos_sensibles=True sin campos EIPD",
         "POST /rats/ con datos_sensibles=True sin evaluacion_impacto+estado_eipd",
         "HTTP 422", "pytest"],
        ["TC-055", "MEDIO",   "Backend",  "Ruta /auditoria/verify-chain no capturada por /{company_id}",
         "GET /rats/auditoria/verify-chain (superadmin)",
         "HTTP 200 con chain info", "pytest"],
    ]
    add_table(doc, ["ID", "Sev.", "Nivel", "Descripción", "Pasos", "Resultado Esperado", "Framework"],
              tc_v111, col_widths_cm=[1.2, 1.3, 1.5, 3.5, 4.5, 3.5, 1.5])

    # 3. TC-056 a TC-063 (v1.12)
    section_heading(doc, "Casos de Prueba v1.12 (Septiembre 2026)", level=1)
    tc_v112 = [
        ["TC-056", "ALTO",    "Backend",  "GET /publico/verificar-titular — sin TKT abierto → 200 {}",
         "GET /publico/verificar-titular?email=sin_ticket@test.com",
         "HTTP 200, tiene_ticket=false", "pytest"],
        ["TC-057", "CRÍTICO", "Backend",  "GET /publico/verificar-titular — con TKT abierto → 200 con datos",
         "GET /publico/verificar-titular?email=con_ticket@test.com",
         "HTTP 200, tiene_ticket=true + datos TKT", "pytest"],
        ["TC-058", "ALTO",    "Backend",  "GET /publico/verificar-titular — email no registrado → 200 {}",
         "GET /publico/verificar-titular?email=desconocido@test.com",
         "HTTP 200, tiene_ticket=false", "pytest"],
        ["TC-059", "ALTO",    "Backend",  "Rate-limit verificar-titular: >10/h por IP → 429",
         "11 peticiones consecutivas desde misma IP",
         "HTTP 429 en la 11.ª", "pytest + rate-limit test"],
        ["TC-060", "ALTO",    "Backend",  "POST /tkt-solicitud-derecho/ → acuse de recibo enviado (mock SMTP)",
         "POST con email válido, SMTP mockeado",
         "acuse_enviado_at != null en response", "pytest + mock"],
        ["TC-061", "MEDIO",   "Backend",  "POST TKT sin email → acuse NO enviado (sin fallo)",
         "POST con titular_email=None",
         "HTTP 201, acuse_enviado_at=null", "pytest"],
        ["TC-062", "ALTO",    "Frontend", "CompanyFichaPanel tabs cargan lazy sin error (4 tabs)",
         "Navegar a /empresas/{id}, clicar cada tab",
         "Contenido visible, sin error 500", "Playwright"],
        ["TC-063", "MEDIO",   "Global",   "Búsqueda de 'solicitante' en codebase → 0 ocurrencias (RNF-21)",
         "grep -r 'solicitante' src/ backend/",
         "0 matches", "CI grep check"],
    ]
    add_table(doc, ["ID", "Sev.", "Nivel", "Descripción", "Pasos", "Resultado Esperado", "Framework"],
              tc_v112, col_widths_cm=[1.2, 1.3, 1.5, 3.5, 4.5, 3.5, 1.5])

    # 4. Resumen de cobertura actualizado
    section_heading(doc, "Resumen de Cobertura Acumulado v1.13", level=1)
    cobertura = [
        ["Backend pytest",    "~740 tests", "pytest + httpx", "TC-001 a TC-063 cubiertos", "0 fallos"],
        ["Frontend TypeScript","0 errores",  "tsc --noEmit",  "Sin regresiones de tipos",  "0 errores"],
        ["E2E Playwright",    "~65 tests",  "Playwright",    "Flows ARCO, EIPD, Brechas",  "OK"],
        ["Integration",       "Neon QA",    "PostgreSQL",    "custodio_test DB",            "OK"],
    ]
    add_table(doc, ["Tipo", "Cantidad", "Framework", "Alcance", "Estado"],
              cobertura, col_widths_cm=[2.5, 1.5, 2.5, 5.5, 2.0])

    dest = rename_to_v113(base)
    if dest.exists():
        dest.unlink()
    doc.save(str(dest))
    if base != dest and base.exists():
        base.unlink()
    print(f"  ✓ {dest.name}")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"=== Generación consolidada {VERSION} ===")
    print(f"OUT_DIR: {OUT_DIR}")

    if not OUT_DIR.exists():
        print(f"ERROR: {OUT_DIR} no existe")
        sys.exit(1)

    consolidar_02_requisitos()
    consolidar_03_historias()
    consolidar_09_backlog()
    consolidar_10_plan_qa()

    print(f"\n✓ Consolidación {VERSION} completada.")
    print("Archivos en docs/documentacion_oficial/:")
    for f in sorted(OUT_DIR.glob("*.docx")):
        print(f"  {f.name}")
