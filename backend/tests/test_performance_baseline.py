"""
Performance baseline — Fase 1 higiene.

Crea 120 RATs para una empresa y mide tiempos de respuesta de los
endpoints criticos del dashboard + reportes. Esto establece un
baseline contra el cual detectar regresiones de performance
(futuros commits que rompan indices, introduzcan N+1, etc.).

Umbrales (tiempos esperados):
- GET /rats/dashboard/{id}         < 1000 ms
- GET /rats/reportes (pagina 1)   < 1500 ms
- GET /rats/reportes (pagina 10)  < 1500 ms
- GET /rats/ (listado)            < 1000 ms
- GET /companies/{id}             < 500 ms (incluye has_politica_transparencia)

Los tests son SKIP si la variable RUN_PERF=1 no esta seteada (no queremos
contaminar las pruebas unitarias normales con bulk inserts).

Uso:
    RUN_PERF=1 pytest tests/test_performance_baseline.py -v -s

Historia: este test existe porque el endpoint GET /rats cayo en produccion
el 2026-07-07 cuando faltaba una migracion SQL. Tener baselines
establecidos ayuda a detectar regresiones silenciosas.
"""
import os
import time

import pytest


# Cantidad de RATs a crear para el baseline
BULK_SIZE = 120

# Umbrales en milisegundos (ms)
THRESHOLDS = {
    "dashboard": 1000,
    "reportes_p1": 1500,
    "reportes_p10": 1500,
    "listar_rats": 1000,
    "company_detail": 500,
}


def _should_run_perf():
    """Skip si RUN_PERF no esta habilitado."""
    return os.environ.get("RUN_PERF") == "1"


@pytest.mark.skipif(
    not _should_run_perf(),
    reason="Performance baseline — set RUN_PERF=1 para ejecutar",
)
class TestPerformanceBaseline:
    """Tests de baseline de performance con 120 RATs."""

    def _create_bulk(self, client, auth_headers, empresa, rat_base):
        """Helper: inserta BULK_SIZE RATs."""
        import json
        created = []
        t0 = time.time()
        for i in range(BULK_SIZE):
            payload = {
                **rat_base,
                "nombre_proceso": f"RAT Perf {i:04d}",
                # Varia nivel de riesgo para queries mas realistas
                "datos_sensibles": (i % 3 == 0),
                "transferencia_internacional": (i % 5 == 0),
            }
            r = client.post("/rats/", json=payload, headers=auth_headers)
            assert r.status_code == 201, f"Failed to create RAT #{i}: {r.text[:200]}"
            created.append(r.json())
        elapsed = time.time() - t0
        print(f"\n[BULK] Created {BULK_SIZE} RATs in {elapsed:.2f}s ({BULK_SIZE/elapsed:.1f} RATs/s)")
        return created

    def test_dashboard_baseline(self, client, auth_headers, empresa, rat_base):
        """GET /rats/dashboard/{company_id} con 120 RATs."""
        self._create_bulk(client, auth_headers, empresa, rat_base)

        t0 = time.time()
        resp = client.get(f"/rats/dashboard/{empresa['id']}", headers=auth_headers)
        elapsed_ms = (time.time() - t0) * 1000

        assert resp.status_code == 200
        body = resp.json()
        assert body["total_procesos"] >= BULK_SIZE

        print(f"\n[METRIC] GET /rats/dashboard/{{id}}: {elapsed_ms:.0f}ms (umbral: {THRESHOLDS['dashboard']}ms)")
        assert elapsed_ms < THRESHOLDS["dashboard"], (
            f"Dashboard performance REGRESION: {elapsed_ms:.0f}ms >= {THRESHOLDS['dashboard']}ms"
        )

    def test_reportes_page1_baseline(self, client, auth_headers, empresa, rat_base):
        """GET /rats/reportes?limit=50 primera pagina."""
        self._create_bulk(client, auth_headers, empresa, rat_base)

        t0 = time.time()
        resp = client.get(
            f"/rats/reportes?company_id={empresa['id']}&skip=0&limit=50",
            headers=auth_headers,
        )
        elapsed_ms = (time.time() - t0) * 1000

        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] >= BULK_SIZE
        assert len(body["rats"]) == 50

        print(f"\n[METRIC] GET /rats/reportes page1: {elapsed_ms:.0f}ms (umbral: {THRESHOLDS['reportes_p1']}ms)")
        assert elapsed_ms < THRESHOLDS["reportes_p1"], (
            f"Reportes p1 performance REGRESION: {elapsed_ms:.0f}ms >= {THRESHOLDS['reportes_p1']}ms"
        )

    def test_reportes_page10_baseline(self, client, auth_headers, empresa, rat_base):
        """GET /rats/reportes?skip=500&limit=50 — pagina profunda."""
        # Crear 600 RATs para que la pagina 10 exista
        bigger_bulk = 6 * BULK_SIZE  # 720
        for i in range(bigger_bulk - BULK_SIZE):
            payload = {**rat_base, "nombre_proceso": f"RAT Extra {i:04d}"}
            client.post("/rats/", json=payload, headers=auth_headers)

        t0 = time.time()
        resp = client.get(
            f"/rats/reportes?company_id={empresa['id']}&skip=550&limit=50",
            headers=auth_headers,
        )
        elapsed_ms = (time.time() - t0) * 1000

        assert resp.status_code == 200

        print(f"\n[METRIC] GET /rats/reportes page10: {elapsed_ms:.0f}ms (umbral: {THRESHOLDS['reportes_p10']}ms)")
        assert elapsed_ms < THRESHOLDS["reportes_p10"], (
            f"Reportes p10 performance REGRESION: {elapsed_ms:.0f}ms >= {THRESHOLDS['reportes_p10']}ms"
        )

    def test_listar_rats_baseline(self, client, auth_headers, empresa, rat_base):
        """GET /rats/?company_id=X — listado sin paginacion."""
        self._create_bulk(client, auth_headers, empresa, rat_base)

        t0 = time.time()
        resp = client.get(f"/rats/?company_id={empresa['id']}", headers=auth_headers)
        elapsed_ms = (time.time() - t0) * 1000

        assert resp.status_code == 200

        print(f"\n[METRIC] GET /rats/?company_id: {elapsed_ms:.0f}ms (umbral: {THRESHOLDS['listar_rats']}ms)")
        assert elapsed_ms < THRESHOLDS["listar_rats"], (
            f"Listar RATs performance REGRESION: {elapsed_ms:.0f}ms >= {THRESHOLDS['listar_rats']}ms"
        )

    def test_company_detail_baseline(self, client, auth_headers, empresa, rat_base):
        """GET /companies/{id} — incluye has_politica_transparencia (introducido 2026-07-07)."""
        self._create_bulk(client, auth_headers, empresa, rat_base)

        t0 = time.time()
        resp = client.get(f"/companies/{empresa['id']}", headers=auth_headers)
        elapsed_ms = (time.time() - t0) * 1000

        assert resp.status_code == 200
        body = resp.json()
        assert "has_politica_transparencia" in body, (
            "Regresion: has_politica_transparencia falta en respuesta — "
            "verificar que el JOIN/round-trip con tabla polizas funciona"
        )

        print(f"\n[METRIC] GET /companies/{{id}}: {elapsed_ms:.0f}ms (umbral: {THRESHOLDS['company_detail']}ms)")
        assert elapsed_ms < THRESHOLDS["company_detail"], (
            f"Company detail performance REGRESION: {elapsed_ms:.0f}ms >= {THRESHOLDS['company_detail']}ms"
        )
