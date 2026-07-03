"""
Tests de ModulePermission â€” feature gates por empresa y modulo.

Cubre:
- Modelo: UNIQUE constraint (company_id, modulo), default enabled=True
- Service: is_module_enabled, get_company_modules, set/bulk update
- Service: require_module_enabled levanta 403 cuando modulo deshabilitado
- Endpoints: GET/PUT acceso por superadmin vs admin_empresa
- Endpoints: solo superadmin puede modificar
"""
import pytest

from app.models.module_permission import ModulePermission, ModuloEnum
from app.services import module_permission_service as svc


# ============================================================
# Service tests
# ============================================================

class TestModulePermissionService:
    def test_is_module_enabled_default_true(self, db, empresa):
        """Sin fila, modulo esta enabled por default (opt-out)."""
        assert svc.is_module_enabled(db, empresa["id"], ModuloEnum.RAT) is True
        assert svc.is_module_enabled(db, empresa["id"], ModuloEnum.ARCO) is True
        assert svc.is_module_enabled(db, empresa["id"], ModuloEnum.BRECHAS) is True

    def test_set_module_enabled_creates_row(self, db, empresa):
        """set_module_enabled crea una fila nueva si no existe."""
        perm = svc.set_module_enabled(db, empresa["id"], ModuloEnum.ARCO, False)
        assert perm.id is not None
        assert perm.enabled is False
        assert perm.modulo == "ARCO"
        assert svc.is_module_enabled(db, empresa["id"], "ARCO") is False

    def test_set_module_enabled_updates_existing(self, db, empresa):
        """set_module_enabled actualiza fila existente (no duplica)."""
        svc.set_module_enabled(db, empresa["id"], "RAT", False)
        svc.set_module_enabled(db, empresa["id"], "RAT", True)
        count = (
            db.query(ModulePermission)
            .filter(
                ModulePermission.company_id == empresa["id"],
                ModulePermission.modulo == "RAT",
            )
            .count()
        )
        assert count == 1
        assert svc.is_module_enabled(db, empresa["id"], "RAT") is True

    def test_set_module_invalid_raises_400(self, db, empresa):
        """Modulo invalido levanta HTTPException 400."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            svc.set_module_enabled(db, empresa["id"], "MODULO_INEXISTENTE", True)
        assert exc_info.value.status_code == 400

    def test_get_company_modules_returns_all(self, db, empresa):
        """get_company_modules retorna todos los modulos (default enabled=True)."""
        mods = svc.get_company_modules(db, empresa["id"])
        assert len(mods) == len(svc.ALL_MODULOS)
        for modulo, enabled in mods.items():
            assert enabled is True

    def test_get_active_modules_filters_disabled(self, db, empresa):
        """get_active_modules excluye los deshabilitados."""
        svc.set_module_enabled(db, empresa["id"], "ARCO", False)
        svc.set_module_enabled(db, empresa["id"], "BRECHAS", False)
        active = svc.get_active_modules(db, empresa["id"])
        assert "ARCO" not in active
        assert "BRECHAS" not in active
        assert "RAT" in active
        assert "EIPD" in active

    def test_bulk_update_multiple(self, db, empresa):
        """bulk_update_modules procesa varios modulos a la vez."""
        updates = {
            "RAT": True,
            "ARCO": False,
            "BRECHAS": False,
        }
        result = svc.bulk_update_modules(db, empresa["id"], updates)
        assert result["RAT"] is True
        assert result["ARCO"] is False
        assert result["BRECHAS"] is False
        assert result["EIPD"] is True  # No tocado, default

    def test_bulk_update_invalid_raises_400(self, db, empresa):
        """bulk_update_modules rechaza modulos invalidos."""
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            svc.bulk_update_modules(db, empresa["id"], {"INVALID": True})
        assert exc_info.value.status_code == 400

    def test_require_module_enabled_passes_when_enabled(self, db, empresa):
        """require_module_enabled NO levanta si modulo esta enabled."""
        svc.require_module_enabled(db, empresa["id"], "RAT")  # No raise

    def test_require_module_enabled_raises_403_when_disabled(self, db, empresa):
        """require_module_enabled levanta 403 si modulo deshabilitado."""
        svc.set_module_enabled(db, empresa["id"], "ARCO", False)
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc_info:
            svc.require_module_enabled(db, empresa["id"], "ARCO")
        assert exc_info.value.status_code == 403


# ============================================================
# Endpoint tests
# ============================================================

class TestModulePermissionsEndpoints:
    def test_get_modules_superadmin_ok(self, client, auth_headers, empresa):
        """GET /module-permissions/{id} como superadmin retorna estado."""
        resp = client.get(f"/module-permissions/{empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["company_id"] == empresa["id"]
        assert "modules" in data
        assert "RAT" in data["modules"]
        assert data["modules"]["RAT"] is True

    def test_get_active_modules_returns_list(self, client, auth_headers, empresa):
        """GET /module-permissions/{id}/active retorna lista."""
        resp = client.get(f"/module-permissions/{empresa['id']}/active", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "active_modules" in data
        assert "RAT" in data["active_modules"]

    def test_toggle_module_superadmin_ok(self, client, auth_headers, db, empresa):
        """PUT /module-permissions/{id}/{modulo} como superadmin togglea."""
        resp = client.put(
            f"/module-permissions/{empresa['id']}/ARCO",
            json={"modulo": "ARCO", "enabled": False},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["enabled"] is False

    def test_bulk_update_superadmin_ok(self, client, auth_headers, empresa):
        """PUT /module-permissions/{id} como superadmin bulk update."""
        resp = client.put(
            f"/module-permissions/{empresa['id']}",
            json={"modules": {"RAT": True, "ARCO": False, "BRECHAS": False}},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["modules"]["RAT"] is True
        assert data["modules"]["ARCO"] is False
        assert data["modules"]["BRECHAS"] is False

    def test_toggle_invalid_modulo_400(self, client, auth_headers, empresa):
        """Modulo invalido retorna 400."""
        resp = client.put(
            f"/module-permissions/{empresa['id']}/INVALID",
            json={"modulo": "INVALID", "enabled": True},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_get_nonexistent_company_404(self, client, auth_headers):
        """GET de empresa inexistente retorna 404."""
        resp = client.get("/module-permissions/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_unauthorized_no_token_401(self, client, empresa):
        """Sin token retorna 401."""
        resp = client.get(f"/module-permissions/{empresa['id']}")
        assert resp.status_code == 401


# ============================================================
# Integration: gate enforcement en rutas criticas
# ============================================================

class TestFeatureGateEnforcement:
    def test_rats_listar_403_when_module_disabled(self, client, auth_headers, db, empresa):
        """GET /rats/ retorna 403 cuando modulo RAT esta deshabilitado."""
        svc.set_module_enabled(db, empresa["id"], "RAT", False)
        resp = client.get(f"/rats/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 403
        assert "RAT" in resp.json()["detail"]

    def test_rats_listar_200_when_module_enabled(self, client, auth_headers, db, empresa):
        """GET /rats/ retorna 200 cuando modulo RAT esta habilitado (default)."""
        resp = client.get(f"/rats/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200

    def test_brechas_listar_403_when_module_disabled(self, client, auth_headers, db, empresa):
        """GET /brechas/ retorna 403 cuando modulo BRECHAS esta deshabilitado."""
        svc.set_module_enabled(db, empresa["id"], "BRECHAS", False)
        resp = client.get(f"/brechas/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 403
        assert "BRECHAS" in resp.json()["detail"]

    def test_brechas_listar_200_when_module_enabled(self, client, auth_headers, db, empresa):
        """GET /brechas/ retorna 200 cuando modulo BRECHAS esta habilitado (default)."""
        resp = client.get(f"/brechas/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200

    def test_tkt_listar_403_when_module_disabled(self, client, auth_headers, db, empresa):
        """GET /tkt-solicitud-derecho/ retorna 403 cuando modulo ARCO esta deshabilitado."""
        svc.set_module_enabled(db, empresa["id"], "ARCO", False)
        resp = client.get(f"/tkt-solicitud-derecho/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 403
        assert "ARCO" in resp.json()["detail"]

    def test_tkt_listar_200_when_module_enabled(self, client, auth_headers, db, empresa):
        """GET /tkt-solicitud-derecho/ retorna 200 cuando ARCO esta habilitado."""
        resp = client.get(f"/tkt-solicitud-derecho/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200

    def test_disabling_rat_does_not_affect_brechas(self, client, auth_headers, db, empresa):
        """Deshabilitar RAT no afecta brechas (modulos son independientes)."""
        svc.set_module_enabled(db, empresa["id"], "RAT", False)
        resp = client.get(f"/brechas/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
        resp = client.get(f"/tkt-solicitud-derecho/?company_id={empresa['id']}", headers=auth_headers)
        assert resp.status_code == 200
