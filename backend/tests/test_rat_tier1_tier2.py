"""
Tests para los 15 campos nuevos de RAT (Tier 1 + Tier 2) - Iter 11.
Cubre models/rat.py, schemas/rat.py y la paridad Pydantic ↔ TypeScript.

 Campos Tier 1 (criticos): datos_nna, nivel_confidencialidad, estructura_dato,
   datos_anonimizados, datos_seudonimizados
 Campos Tier 2 (operativos): ciclo_procesamiento, automatizacion, frecuencia,
   transferencia_nacional, doc_clausulas, medidas_organizativas,
   mecanismos_eliminacion, tecnica_anonimizacion, origen_dato_portabilidad,
   fecha_levantamiento
"""
import pytest
from datetime import date

from app.models.rat import RAT


class TestRATTier1Tier2Schema:
    """Tests directos de schemas Pydantic (sin endpoint)."""

    def test_schema_acepta_todos_los_campos_nuevos(self):
        """Valida que RATCreate acepta los 15 campos sin error."""
        from app.schemas.rat import RATCreate
        data = RATCreate(
            company_id=1,
            nombre_proceso="Test proceso",
            categoria_datos="Nombre, email",
            finalidad="Gestión de clientes",
            base_legal="Consentimiento del titular",
            fuente_datos="Del propio titular",
            plazo_retencion="5 años",
            # Tier 1
            datos_nna="ninguno",
            nivel_confidencialidad="DC1",
            estructura_dato="estructurado",
            datos_anonimizados=True,
            datos_seudonimizados=False,
            # Tier 2
            ciclo_procesamiento="almacenamiento",
            automatizacion="100% automatizado",
            frecuencia="mensual",
            transferencia_nacional=True,
            doc_clausulas="Política de privacidad en web",
            medidas_organizativas="Designación RAI",
            mecanismos_eliminacion="Borrado seguro NIST 800-88",
            tecnica_anonimizacion="seudonimizacion",
            origen_dato_portabilidad="Directamente del titular",
            fecha_levantamiento="2026-01-15",
        )
        assert data.datos_nna == "ninguno"
        assert data.nivel_confidencialidad == "DC1"
        assert data.estructura_dato == "estructurado"
        assert data.datos_anonimizados is True
        assert data.datos_seudonimizados is False
        assert data.ciclo_procesamiento == "almacenamiento"
        assert data.automatizacion == "100% automatizado"
        assert data.frecuencia == "mensual"
        assert data.transferencia_nacional is True
        assert data.doc_clausulas == "Política de privacidad en web"
        assert data.medidas_organizativas == "Designación RAI"
        assert data.mecanismos_eliminacion == "Borrado seguro NIST 800-88"
        assert data.tecnica_anonimizacion == "seudonimizacion"
        assert data.origen_dato_portabilidad == "Directamente del titular"
        assert data.fecha_levantamiento == date(2026, 1, 15)

    def test_schema_acepta_campos_nulos(self):
        """Todos los campos nuevos son opcionales (None por defecto)."""
        from app.schemas.rat import RATCreate
        data = RATCreate(
            company_id=1,
            nombre_proceso="Test sin campos nuevos",
            categoria_datos="Nombre",
            finalidad="Test",
            base_legal="Consentimiento del titular",
            fuente_datos="Web",
            plazo_retencion="1 año",
        )
        assert data.datos_nna is None
        assert data.nivel_confidencialidad is None
        assert data.estructura_dato is None
        assert data.datos_anonimizados is False
        assert data.datos_seudonimizados is False
        assert data.ciclo_procesamiento is None
        assert data.automatizacion is None
        assert data.frecuencia is None
        assert data.transferencia_nacional is False
        assert data.doc_clausulas is None
        assert data.medidas_organizativas is None
        assert data.mecanismos_eliminacion is None
        assert data.tecnica_anonimizacion is None
        assert data.origen_dato_portabilidad is None
        assert data.fecha_levantamiento is None

    def test_schema_acepta_todos_los_valores_nna(self):
        """datos_nna acepta: ninguno, ninos, adolescentes, ambos."""
        from app.schemas.rat import RATCreate
        for val in ["ninguno", "ninos", "adolescentes", "ambos"]:
            data = RATCreate(
                company_id=1,
                nombre_proceso="Test",
                categoria_datos="Test",
                finalidad="Test",
                base_legal="Consentimiento del titular",
                fuente_datos="Web",
                plazo_retencion="1 año",
                datos_nna=val,
            )
            assert data.datos_nna == val

    def test_schema_acepta_todos_los_valores_dc(self):
        """nivel_confidencialidad acepta: DC0, DC1, DC2, DC3."""
        from app.schemas.rat import RATCreate
        for val in ["DC0", "DC1", "DC2", "DC3"]:
            data = RATCreate(
                company_id=1,
                nombre_proceso="Test",
                categoria_datos="Test",
                finalidad="Test",
                base_legal="Consentimiento del titular",
                fuente_datos="Web",
                plazo_retencion="1 año",
                nivel_confidencialidad=val,
            )
            assert data.nivel_confidencialidad == val

    def test_schema_acepta_todas_estructuras_dato(self):
        """estructura_dato acepta los 4 valores."""
        from app.schemas.rat import RATCreate
        for val in ["estructurado", "semiestructurado", "no_estructurado", "fisico"]:
            data = RATCreate(
                company_id=1,
                nombre_proceso="Test",
                categoria_datos="Test",
                finalidad="Test",
                base_legal="Consentimiento del titular",
                fuente_datos="Web",
                plazo_retencion="1 año",
                estructura_dato=val,
            )
            assert data.estructura_dato == val

    def test_schema_rat_update_tambien_soporta_los_campos(self):
        """RATUpdate acepta los 15 campos nuevos."""
        from app.schemas.rat import RATUpdate
        update = RATUpdate(
            datos_nna="ninos",
            nivel_confidencialidad="DC3",
            estructura_dato="semiestructurado",
            datos_anonimizados=True,
            datos_seudonimizados=True,
            ciclo_procesamiento="uso",
            automatizacion="mayoritariamente automatizado",
            frecuencia="diaria",
            transferencia_nacional=True,
            doc_clausulas="Aviso de privacidad",
            medidas_organizativas="Procedimiento de acceso",
            mecanismos_eliminacion="Destrucción física",
            tecnica_anonimizacion="k-anonimidad",
            origen_dato_portabilidad="De otro responsable",
            fecha_levantamiento="2026-03-01",
        )
        assert update.datos_nna == "ninos"
        assert update.nivel_confidencialidad == "DC3"
        assert update.estructura_dato == "semiestructurado"
        assert update.datos_anonimizados is True
        assert update.datos_seudonimizados is True
        assert update.ciclo_procesamiento == "uso"
        assert update.automatizacion == "mayoritariamente automatizado"
        assert update.frecuencia == "diaria"
        assert update.transferencia_nacional is True
        assert update.doc_clausulas == "Aviso de privacidad"
        assert update.medidas_organizativas == "Procedimiento de acceso"
        assert update.mecanismos_eliminacion == "Destrucción física"
        assert update.tecnica_anonimizacion == "k-anonimidad"
        assert update.origen_dato_portabilidad == "De otro responsable"
        assert update.fecha_levantamiento == date(2026, 3, 1)

    def test_schema_fecha_levantamiento_type_date(self):
        """fecha_levantamiento se parsea como date, no string."""
        from app.schemas.rat import RATCreate
        data = RATCreate(
            company_id=1,
            nombre_proceso="Test",
            categoria_datos="Test",
            finalidad="Test",
            base_legal="Consentimiento del titular",
            fuente_datos="Web",
            plazo_retencion="1 año",
            fecha_levantamiento="2026-06-25",
        )
        assert isinstance(data.fecha_levantamiento, date)
        assert data.fecha_levantamiento == date(2026, 6, 25)


class TestRATTier1Tier2Persistence:
    """Tests de persistencia via ORM (db fixture)."""

    def test_crear_rat_con_15_campos_nuevos(self, client, auth_headers, empresa, db, rat_base):
        """Crea un RAT con los 15 campos nuevos via POST /rats/ y verifica persistencia."""
        payload = {**rat_base}
        payload.update(
            datos_nna="ninos",
            nivel_confidencialidad="DC2",
            estructura_dato="estructurado",
            datos_anonimizados=False,
            datos_seudonimizados=True,
            ciclo_procesamiento="comunicacion",
            automatizacion="100% manual",
            frecuencia="anual",
            transferencia_nacional=True,
            doc_clausulas="Cláusula de privacidad en contrato",
            medidas_organizativas="DPO designado",
            mecanismos_eliminacion="Borrado seguro",
            tecnica_anonimizacion="agregacion",
            origen_dato_portabilidad="De otro responsable",
            fecha_levantamiento="2026-01-10",
        )
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        if resp.status_code != 201:
            pytest.fail(f"POST /rats/ falló: {resp.status_code} {resp.text}")
        rat_id = resp.json()["id"]
        rat = db.query(RAT).filter(RAT.id == rat_id).first()
        assert rat is not None
        assert rat.datos_nna == "ninos"
        assert rat.nivel_confidencialidad == "DC2"
        assert rat.estructura_dato == "estructurado"
        assert rat.datos_anonimizados is False
        assert rat.datos_seudonimizados is True
        assert rat.ciclo_procesamiento == "comunicacion"
        assert rat.automatizacion == "100% manual"
        assert rat.frecuencia == "anual"
        assert rat.transferencia_nacional is True
        assert rat.doc_clausulas == "Cláusula de privacidad en contrato"
        assert rat.medidas_organizativas == "DPO designado"
        assert rat.mecanismos_eliminacion == "Borrado seguro"
        assert rat.tecnica_anonimizacion == "agregacion"
        assert rat.origen_dato_portabilidad == "De otro responsable"
        assert rat.fecha_levantamiento == date(2026, 1, 10)

    def test_get_rat_retorna_15_campos(self, client, auth_headers, empresa, db, rat_base):
        """GET /rats/{id} retorna los 15 campos nuevos en el JSON."""
        payload = {**rat_base}
        payload.update(
            datos_nna="adolescentes",
            nivel_confidencialidad="DC3",
            estructura_dato="no_estructurado",
            datos_anonimizados=True,
            datos_seudonimizados=False,
            ciclo_procesamiento="eliminacion",
            automatizacion="mayoritariamente automatizado",
            frecuencia="trimestral",
            transferencia_nacional=False,
            doc_clausulas="Política de tratamiento",
            medidas_organizativas="Control de acceso",
            mecanismos_eliminacion="Destrucción física certificados",
            tecnica_anonimizacion="perturbacion",
            origen_dato_portabilidad="Directamente del titular",
            fecha_levantamiento="2026-02-20",
        )
        resp = client.post("/rats/", json=payload, headers=auth_headers)
        if resp.status_code != 201:
            pytest.fail(f"POST /rats/ falló: {resp.status_code} {resp.text}")
        rat_id = resp.json()["id"]
        resp2 = client.get(f"/rats/{rat_id}", headers=auth_headers)
        if resp2.status_code != 200:
            pytest.fail(f"GET /rats/{rat_id} falló: {resp2.status_code}")
        json_data = resp2.json()
        assert json_data["datos_nna"] == "adolescentes"
        assert json_data["nivel_confidencialidad"] == "DC3"
        assert json_data["estructura_dato"] == "no_estructurado"
        assert json_data["datos_anonimizados"] is True
        assert json_data["datos_seudonimizados"] is False
        assert json_data["ciclo_procesamiento"] == "eliminacion"
        assert json_data["automatizacion"] == "mayoritariamente automatizado"
        assert json_data["frecuencia"] == "trimestral"
        assert json_data["transferencia_nacional"] is False
        assert json_data["doc_clausulas"] == "Política de tratamiento"
        assert json_data["medidas_organizativas"] == "Control de acceso"
        assert json_data["mecanismos_eliminacion"] == "Destrucción física certificados"
        assert json_data["tecnica_anonimizacion"] == "perturbacion"
        assert json_data["origen_dato_portabilidad"] == "Directamente del titular"
        assert json_data["fecha_levantamiento"] == "2026-02-20"

    def test_update_rat_modifica_15_campos(self, client, auth_headers, empresa, db, rat_base):
        """PUT /rats/{id} modifica los 15 campos nuevos."""
        resp = client.post("/rats/", json=rat_base, headers=auth_headers)
        if resp.status_code != 201:
            pytest.fail(f"POST /rats/ falló: {resp.status_code} {resp.text}")
        rat_id = resp.json()["id"]
        update_payload = {
            "datos_nna": "ambos",
            "nivel_confidencialidad": "DC1",
            "estructura_dato": "fisico",
            "datos_anonimizados": True,
            "datos_seudonimizados": True,
            "ciclo_procesamiento": "archivo",
            "automatizacion": "100% automatizado",
            "frecuencia": "puntual",
            "transferencia_nacional": True,
            "doc_clausulas": "Términos y condiciones",
            "medidas_organizativas": "Auditoría anual",
            "mecanismos_eliminacion": "Devolución a proveedor",
            "tecnica_anonimizacion": "pseudonimizacion",
            "origen_dato_portabilidad": "Fuentes públicas",
            "fecha_levantamiento": "2026-05-01",
        }
        resp2 = client.put(f"/rats/{rat_id}", json=update_payload, headers=auth_headers)
        if resp2.status_code != 200:
            pytest.fail(f"PUT /rats/{rat_id} falló: {resp2.status_code} {resp2.text}")
        rat = db.query(RAT).filter(RAT.id == rat_id).first()
        assert rat.datos_nna == "ambos"
        assert rat.nivel_confidencialidad == "DC1"
        assert rat.estructura_dato == "fisico"
        assert rat.datos_anonimizados is True
        assert rat.datos_seudonimizados is True
        assert rat.ciclo_procesamiento == "archivo"
        assert rat.automatizacion == "100% automatizado"
        assert rat.frecuencia == "puntual"
        assert rat.transferencia_nacional is True
        assert rat.doc_clausulas == "Términos y condiciones"
        assert rat.medidas_organizativas == "Auditoría anual"
        assert rat.mecanismos_eliminacion == "Devolución a proveedor"
        assert rat.tecnica_anonimizacion == "pseudonimizacion"
        assert rat.origen_dato_portabilidad == "Fuentes públicas"
        assert rat.fecha_levantamiento == date(2026, 5, 1)
