"""
Tests CRUD de registros RAT.
Cubre: creaciÃ³n, listado, obtenciÃ³n, actualizaciÃ³n de estado, eliminaciÃ³n,
completitud, flags de riesgo y casos edge.
"""



class TestCrearRAT:
    def test_crear_rat_completo(self, client, auth_headers, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["nombre_proceso"] == rat_base["nombre_proceso"]
        # El servicio marca automÃ¡ticamente como "completo" si todos los campos
        # obligatorios estÃ¡n presentes (comportamiento por diseÃ±o)
        assert data["estado"] in ("borrador", "completo")
        assert "id" in data
        assert "completitud" in data
        assert isinstance(data["completitud"], int)

    def test_crear_rat_sin_nombre_falla(self, client, auth_headers, rat_base):
        payload = {**rat_base, "nombre_proceso": ""}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 422

    def test_crear_rat_sin_company_falla(self, client, auth_headers, rat_base):
        payload = {k: v for k, v in rat_base.items() if k != "company_id"}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 422

    def test_crear_rat_company_inexistente_falla(self, client, auth_headers, rat_base):
        payload = {**rat_base, "company_id": 99999}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code in (404, 400)

    def test_crear_rat_con_datos_sensibles(self, client, auth_headers, rat_base):
        payload = {**rat_base, "datos_sensibles": True, "tipo_dato_sensible": "Salud (física o mental)", "evaluacion_impacto": True, "estado_eipd": "pendiente"}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["datos_sensibles"] is True
        assert data["evaluacion_impacto"] is True

    def test_crear_rat_base_legal_otra_sin_archivo_falla(self, client, auth_headers, rat_base):
        """H1.1 — base_legal='Otra' sin archivo adjunto debe fallar con 422 (Art. 11+16 Ley 21.719)."""
        payload = {**rat_base, "base_legal": "Otra"}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 422
        detail = resp.json().get("detail", "")
        assert "documento adjunto" in detail.lower() or "archivo" in detail.lower()

    def test_crear_rat_base_legal_otra_con_archivo_ok(self, client, auth_headers, rat_base):
        """base_legal='Otra' con archivo adjunto debe pasar (H1.1)."""
        import base64
        pdf_b64 = base64.b64encode(b"%PDF-1.4\nfake\n%%EOF").decode()
        payload = {
            **rat_base,
            "base_legal": "Otra",
            "archivo_base_legal_base64": pdf_b64,
            "archivo_base_legal_nombre": "base_legal_otra.pdf",
            "archivo_base_legal_tipo": "application/pdf",
        }
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 201

    def test_crear_rat_con_transferencia_internacional(self, client, auth_headers, rat_base):
        payload = {**rat_base, "transferencia_internacional": True, "garantias_transferencia_int": "Cláusulas contractuales tipo", "evaluacion_impacto": True, "estado_eipd": "pendiente", "pais_destino": "Estados Unidos"}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["pais_destino"] == "Estados Unidos"

    def test_crear_rat_sin_auth_falla(self, client, rat_base):
        resp = client.post("/rats/", json=rat_base)
        assert resp.status_code in (401, 403)

    def test_nombre_proceso_espacios_vacios_falla(self, client, auth_headers, rat_base):
        payload = {**rat_base, "nombre_proceso": "   "}
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        assert resp.status_code == 422


class TestListarRATs:
    def test_listar_por_empresa(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get(f"/rats/?company_id={rat_base['company_id']}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(r["company_id"] == rat_base["company_id"] for r in data)

    def test_listar_sin_filtro(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get("/rats/", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_listar_empresa_sin_rats(self, client, auth_headers, empresa):
        resp = client.get(f"/rats/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_listar_todos_tienen_completitud(self, client, auth_headers, rat_base):
        client.post("/rats/", json=rat_base, headers=auth_headers)
        resp = client.get("/rats/", headers=auth_headers)
        assert resp.status_code == 200
        for r in resp.json():
            assert "completitud" in r
            assert 0 <= r["completitud"] <= 100


class TestObtenerRAT:
    def test_obtener_existente(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.get(f"/rats/{created['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    def test_obtener_inexistente_404(self, client, auth_headers):
        resp = client.get("/rats/99999", headers=auth_headers)
        assert resp.status_code == 404


class TestActualizarRAT:
    def test_actualizar_nombre_proceso(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.put(
            f"/rats/{created['id']}",
            json={"nombre_proceso": "Proceso Actualizado"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["nombre_proceso"] == "Proceso Actualizado"

    def test_cambiar_estado_a_en_revision(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.put(
            f"/rats/{created['id']}",
            json={"estado": "en_revision"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["estado"] == "en_revision"

    def test_cambiar_estado_a_aprobado(self, client, auth_headers, rat_base):
        import base64
        pdf_b64 = base64.b64encode(b"%PDF-1.4\nfake\n%%EOF").decode()
        completo = {**rat_base, "transferencia_datos": "No aplica", "datos_nna": "No aplica",
            "nivel_confidencialidad": "Alta", "estructura_dato": "Digital",
            "datos_anonimizados": False, "datos_seudonimizados": True,
            "sistema_almacenamiento": "Base de datos segura", "volumen_titulares_estimado": 1000,
            "responsable_tratamiento_email": "dpo@empresa.cl",
            "ciclo_procesamiento": "Recurrente", "automatizacion": "Parcialmente automatizado",
            "frecuencia": "Diaria", "transferencia_nacional": False,
            "doc_clausulas": "Clausula de proteccion de datos",
            "medidas_organizativas": "Controles de acceso basados en roles",
            "mecanismos_eliminacion": "Eliminacion segura tras plazo",
            "tecnica_anonimizacion": "No aplica", "origen_dato_portabilidad": "Portal web",
            "archivo_base_legal_base64": pdf_b64,
            "archivo_base_legal_nombre": "consentimiento.pdf",
            "archivo_base_legal_tipo": "application/pdf"}
        created = client.post("/rats/", json=completo, headers=auth_headers).json()
        resp = client.post(f"/rats/{created['id']}/aprobar", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["estado"] == "aprobado"
        assert data["aprobado_por"] is not None
        assert data["fecha_aprobacion"] is not None

    def test_estado_invalido_falla(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.put(
            f"/rats/{created['id']}",
            json={"estado": "estado_inventado"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_actualizar_inexistente_404(self, client, auth_headers):
        resp = client.put("/rats/99999", json={"nombre_proceso": "X"}, headers=auth_headers)
        assert resp.status_code == 404

    def test_completitud_aumenta_al_completar(self, client, auth_headers, rat_base):
        """Un RAT con mÃ¡s campos completos debe tener mayor completitud."""
        # RAT base (sin medidas_seguridad ni algunos campos)
        payload_incompleto = {**rat_base}
        payload_incompleto.pop("medidas_seguridad", None)

        created = client.post("/rats/", json=payload_incompleto, headers=auth_headers).json()
        completitud_inicial = created["completitud"]

        resp = client.put(
            f"/rats/{created['id']}",
            json={"medidas_seguridad": "Cifrado AES-256", "observaciones_auditoria": "Sin observaciones"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["completitud"] >= completitud_inicial


class TestEliminarRAT:
    def test_eliminar_existente(self, client, auth_headers, rat_base):
        created = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        resp = client.delete(f"/rats/{created['id']}", headers=auth_headers)
        assert resp.status_code == 200

        check = client.get(f"/rats/{created['id']}", headers=auth_headers)
        assert check.status_code == 404

    def test_eliminar_inexistente_404(self, client, auth_headers):
        resp = client.delete("/rats/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_empresa_eliminada_borra_rats(self, client, auth_headers, rat_base, empresa):
        """EliminaciÃ³n en cascada: al borrar empresa, sus RATs desaparecen."""
        rat = client.post("/rats/", json=rat_base, headers=auth_headers).json()
        rat_id = rat["id"]

        client.delete(f"/companies/{empresa['id']}", headers=auth_headers)

        check = client.get(f"/rats/{rat_id}", headers=auth_headers)
        assert check.status_code == 404


class TestCompletitud:
    def test_completitud_entre_0_y_100(self, client, auth_headers, rat_base):
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        assert resp.status_code == 201
        pct = resp.json()["completitud"]
        assert 0 <= pct <= 100
        def test_rat_con_todos_los_campos_alta_completitud(self, client, auth_headers, rat_base):
            payload = {
                **rat_base,
                "categoria_titulares": "Clientes del servicio web",
                "medidas_seguridad": "Cifrado AES-256",
                "destinatarios": "Equipo comercial",
                "transferencia_internacional": True,
                "pais_destino": "España",
                "garantias_transferencia_int": "Cláusulas Contractuales Tipo (SCC)",
                "datos_sensibles": False,
                "evaluacion_impacto": True,
                "estado_eipd": "pendiente",
                "decisiones_automatizadas": False,
                "observaciones_auditoria": "Proceso auditado y aprobado",
                "transferencia_datos": "Proveedor de email marketing",
            }
            resp = client.post("/rats/", json=payload, headers=auth_headers)
            assert resp.status_code == 201
            # Solo Art. 16 (7+3=10) poblados -> 10/25 = 40%
            pct = resp.json()["completitud"]
            assert pct == 40, f"Esperado 40% (10/25), obtuvo {pct}%"
        def test_rat_minimo_obligatorios_sin_recomendados(self, client, auth_headers, rat_base):
            """Solo con los 7 obligatorios Art. 16: 7/25 = 28%."""
            resp = client.post("/rats/", json=rat_base, headers=auth_headers)
            assert resp.status_code == 201
            pct = resp.json()["completitud"]
            assert pct == 28, f"Esperado 28% (7/25), obtuvo {pct}%"
        def test_rat_con_tier1_tier2_completos_100_porciento(self, client, auth_headers, rat_base):
            """Con los 25 campos poblados (7+3+5+10) debe dar 100%."""
            payload = {
                **rat_base,
                "categoria_titulares": "Clientes del servicio web",
                "medidas_seguridad": "Cifrado AES-256",
                "destinatarios": "Equipo comercial",
                "transferencia_datos": "Proveedor de email marketing",
                "nivel_confidencialidad": "DC2",
                "estructura_dato": "estructurado",
                "datos_nna": "ninguno",
                "datos_anonimizados": False,
                "datos_seudonimizados": False,
                "sistema_almacenamiento": "PostgreSQL on-prem",
                "volumen_titulares_estimado": 5000,
                "responsable_tratamiento_email": "dpo@empresa.cl",
                "ciclo_procesamiento": "Captura → Almacenamiento → Archivo",
                "automatizacion": "asistido",
                "frecuencia": "diaria",
                "transferencia_nacional": False,
                "doc_clausulas": "DPA conforme Art. 14 quater",
                "medidas_organizativas": "RBAC + aprobación dual",
                "mecanismos_eliminacion": "Supresión lógica + verificación",
            }
            resp = client.post("/rats/", json=payload, headers=auth_headers)
            assert resp.status_code == 201
            pct = resp.json()["completitud"]
            assert pct == 100, f"Esperado 100% (25/25), obtuvo {pct}%"
        def test_estado_completo_solo_con_alta_completitud(self, client, auth_headers, rat_base):
            """El estado 'completo' requiere obligatorios + >=90% completitud."""
            payload = {
                **rat_base,
                "categoria_titulares": "Clientes",
                "medidas_seguridad": "TLS 1.3",
                "destinatarios": "Equipo interno",
                "transferencia_datos": "N/A",
                "nivel_confidencialidad": "DC2",
                "estructura_dato": "estructurado",
                "datos_nna": "ninguno",
                "datos_anonimizados": False,
                "datos_seudonimizados": False,
                "sistema_almacenamiento": "PostgreSQL",
                "volumen_titulares_estimado": 1000,
                "responsable_tratamiento_email": "dpo@empresa.cl",
                "ciclo_procesamiento": "Captura → Archivo",
                "automatizacion": "automatico",
                "frecuencia": "diaria",
                "transferencia_nacional": False,
                "doc_clausulas": "N/A",
                "medidas_organizativas": "RBAC",
                "mecanismos_eliminacion": "Supresión",
            }
            resp = client.post("/rats/", json=payload, headers=auth_headers)
            assert resp.status_code == 201
            body = resp.json()
            assert body["completitud"] == 100
            # Estado debe ser 'completo' porque tiene 100% completitud
            assert body["estado"] == "completo", f"Esperado 'completo', obtuvo '{body['estado']}'"


class TestAuditoriaVerifyChain:
    """H2.2 — Solo SUPERADMIN puede verificar la cadena de auditoria global."""

    def test_verify_chain_sin_auth_falla_401(self, client):
        resp = client.get("/rats/auditoria/verify-chain")
        assert resp.status_code == 401

    def test_verify_chain_admin_empresa_falla_403(self, client, db, empresa):
        """admin_empresa NO debe poder verificar la cadena global (H2.2)."""
        from app.models.user import User
        from app.models.user_company import UserCompany, RolEmpresa
        from app.core.security import get_password_hash

        admin_emp = User(
            username="admin_emp_vc_test",
            email="admin_emp_vc@test.cl",
            full_name="Admin Empresa VC",
            hashed_password=get_password_hash("pass1234"),
            is_active=True,
            is_admin=False,
            rol_global="admin_empresa",
        )
        db.add(admin_emp)
        db.commit()
        db.refresh(admin_emp)
        uc = UserCompany(user_id=admin_emp.id, company_id=empresa["id"], rol=RolEmpresa.ADMIN)
        db.add(uc)
        db.commit()

        login = client.post("/auth/login", json={"username": "admin_emp_vc_test", "password": "pass1234"})
        token = login.json()["access_token"]
        resp = client.get("/rats/auditoria/verify-chain", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403