"""
Tests End-to-End: flujos completos como los haría un usuario real.
Simula: login → crear empresa → crear RAT → ver dashboard → exportar.
"""

import pytest


class TestFlujoCompletoUsuario:
    """
    Flujo 1: Usuario nuevo crea empresa, agrega RATs y exporta.
    """

    def test_flujo_completo(self, client, admin_user):
        # 1. Login
        login = client.post("/auth/login", json={"username": "admin", "password": "admin1234"})
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Crear empresa
        empresa = client.post("/companies/", json={
            "nombre": "Clínica E2E Ltda.",
            "rut": "77.888.999-0",
            "rubro": "Salud",
            "contacto_dpo": "Dr. Test",
            "email_dpo": "dpo@clinica.cl",
        }, headers=headers)
        assert empresa.status_code == 201
        company_id = empresa.json()["id"]

        # 3. Obtener sugerencia automática
        sugerencia = client.post("/rats/sugerencias", json={"tipo_proceso": "pacientes"}, headers=headers)
        assert sugerencia.status_code == 200
        sug = sugerencia.json()

        # 4. Crear RAT con datos de sugerencia
        rat = client.post("/rats/", json={
            "company_id": company_id,
            "nombre_proceso": "Gestión de Pacientes",
            "categoria_datos": sug["categoria_datos"],
            "finalidad": sug["finalidad"],
            "base_legal": sug["base_legal"],
            "fuente_datos": "El propio paciente en admisión",
            "plazo_retencion": sug["plazo_retencion_sugerido"],
            "medidas_seguridad": "Acceso restringido a personal médico",
            "datos_sensibles": sug["datos_sensibles"],
            "evaluacion_impacto": False,
            "transferencia_internacional": False,
        }, headers=headers)
        assert rat.status_code == 201
        rat_id = rat.json()["id"]
        # El servicio puede marcar el RAT como "completo" automáticamente si tiene todos los campos
        assert rat.json()["estado"] in ("borrador", "completo")

        # 5. Forzar estado a "aprobado"
        update = client.put(f"/rats/{rat_id}", json={"estado": "aprobado"}, headers=headers)
        assert update.status_code == 200
        assert update.json()["estado"] == "aprobado"

        # 6. Ver dashboard
        dashboard = client.get(f"/rats/dashboard/{company_id}", headers=headers)
        assert dashboard.status_code == 200
        stats = dashboard.json()
        assert stats["total_procesos"] == 1
        assert sum(stats["por_estado"].values()) == 1

        # 7. Exportar CSV
        csv_resp = client.get(f"/rats/export/csv?company_id={company_id}", headers=headers)
        assert csv_resp.status_code == 200
        assert b"Gesti" in csv_resp.content  # "Gestión" puede variar encoding

        # 8. Exportar PDF
        pdf_resp = client.get(f"/rats/export/pdf?company_id={company_id}", headers=headers)
        assert pdf_resp.status_code == 200
        assert pdf_resp.content[:4] == b"%PDF"

        # 9. Eliminar RAT
        del_rat = client.delete(f"/rats/{rat_id}", headers=headers)
        assert del_rat.status_code == 200

        check = client.get(f"/rats/{rat_id}", headers=headers)
        assert check.status_code == 404

        # 10. Eliminar empresa (cascade)
        del_emp = client.delete(f"/companies/{company_id}", headers=headers)
        assert del_emp.status_code == 200


class TestFlujoMultiplesEmpresas:
    """
    Flujo 2: Múltiples empresas con RATs aislados.
    Los RATs de una empresa no deben aparecer en la otra.
    """

    def test_aislamiento_entre_empresas(self, client, auth_headers):
        # Crear empresa A
        emp_a = client.post("/companies/", json={"nombre": "Empresa A", "rut": "11.111.111-1"}, headers=auth_headers)
        assert emp_a.status_code == 201
        id_a = emp_a.json()["id"]

        # Crear empresa B
        emp_b = client.post("/companies/", json={"nombre": "Empresa B", "rut": "22.222.222-2"}, headers=auth_headers)
        assert emp_b.status_code == 201
        id_b = emp_b.json()["id"]

        rat_payload = {
            "nombre_proceso": "Proceso A",
            "categoria_datos": "Email",
            "finalidad": "Marketing",
            "base_legal": "Consentimiento del titular",
            "fuente_datos": "Formulario web",
            "plazo_retencion": "2 años",
        }

        # Crear RAT solo en empresa A
        client.post("/rats/", json={**rat_payload, "company_id": id_a}, headers=auth_headers)

        # Los RATs de empresa B deben ser 0
        rats_b = client.get(f"/rats/?company_id={id_b}", headers=auth_headers)
        assert rats_b.status_code == 200
        assert rats_b.json() == []

        # Dashboard de empresa B: total = 0
        dash_b = client.get(f"/rats/dashboard/{id_b}", headers=auth_headers)
        assert dash_b.json()["total_procesos"] == 0

        # Dashboard de empresa A: total = 1
        dash_a = client.get(f"/rats/dashboard/{id_a}", headers=auth_headers)
        assert dash_a.json()["total_procesos"] == 1


class TestFlujoEdgeCases:
    """
    Flujo 3: Casos límite que pueden romper el sistema en producción.
    """

    def test_crear_multiples_rats_misma_empresa(self, client, auth_headers, empresa):
        payload_base = {
            "company_id": empresa["id"],
            "categoria_datos": "Email",
            "finalidad": "Uso interno",
            "base_legal": "Consentimiento del titular",
            "fuente_datos": "Formulario",
            "plazo_retencion": "1 año",
        }
        nombres = ["Proceso A", "Proceso B", "Proceso C", "Proceso D", "Proceso E"]
        ids = []
        for nombre in nombres:
            r = client.post("/rats/", json={**payload_base, "nombre_proceso": nombre}, headers=auth_headers)
            assert r.status_code == 201
            ids.append(r.json()["id"])

        resp = client.get(f"/rats/?company_id={empresa['id']}", headers=auth_headers)
        assert len(resp.json()) >= 5

        dash = client.get(f"/rats/dashboard/{empresa['id']}", headers=auth_headers)
        assert dash.json()["total_procesos"] >= 5

    def test_nombre_proceso_con_caracteres_especiales(self, client, auth_headers, empresa):
        payload = {
            "company_id": empresa["id"],
            "nombre_proceso": "Gestión & Análisis de Clínicas (Región Ñuble)",
            "categoria_datos": "Datos médicos",
            "finalidad": "Atención clínica",
            "base_legal": "Obligación legal",
            "fuente_datos": "Paciente",
            "plazo_retencion": "10 años",
        }
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert "Gestión" in resp.json()["nombre_proceso"]

    def test_actualizacion_parcial_no_borra_otros_campos(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        original_categoria = created["categoria_datos"]

        # Solo actualizar el nombre
        client.put(
            f"/rats/{created['id']}",
            json={"nombre_proceso": "Nuevo nombre"},
            headers=auth_headers,
        )

        # Verificar que categoria_datos no cambió
        rat = client.get(f"/rats/{created['id']}", headers=auth_headers).json()
        assert rat["categoria_datos"] == original_categoria
        assert rat["nombre_proceso"] == "Nuevo nombre"

    def test_exportar_csv_multiples_rats(self, client, auth_headers, empresa):
        payload_base = {
            "company_id": empresa["id"],
            "categoria_datos": "Nombre, email",
            "finalidad": "Test",
            "base_legal": "Consentimiento del titular",
            "fuente_datos": "Web",
            "plazo_retencion": "1 año",
        }
        for i in range(3):
            client.post("/rats/", json={**payload_base, "nombre_proceso": f"Proceso {i}"}, headers=auth_headers)

        resp = client.get(f"/rats/export/csv?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        content = resp.content.decode("utf-8-sig")
        # Debe haber al menos 3 filas de datos (más la cabecera)
        lines = [l for l in content.splitlines() if l.strip()]
        assert len(lines) >= 4  # 1 cabecera + 3 RATs
