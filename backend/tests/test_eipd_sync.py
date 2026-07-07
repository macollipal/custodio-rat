"""
Tests para la sincronización RAT.estado_eipd ↔ EIPD.resultado (Art. 15 bis).

Cubre:
- Al crear un EIPD, el campo rat.estado_eipd queda sincronizado con eipd.resultado.
- Al actualizar el resultado del EIPD (PUT), el rat.estado_eipd se actualiza.
- El mapeo de enums es correcto: completada/en_proceso/no_requerida.

Estos tests requieren PostgreSQL (Neon QA). Ver backend/CLAUDE.md.
"""
import pytest

from app.models.eipd import ResultadoEIPD
from app.models.rat import EstadoEIPD, EstadoRAT
from app.schemas.eipd import EIPDCreate, EIPDUpdate
from app.services.eipd_service import crear_eipd, actualizar_eipd


@pytest.fixture
def rat_con_sensibles(db, empresa):
    """Crea un RAT con datos_sensibles=True para que la lógica de EIPD aplique."""
    from app.models.rat import RAT

    rat = RAT(
        company_id=empresa["id"],
        nombre_proceso="Proceso sensible test",
        categoria_datos="dato sensible",
        categoria_titulares="titulares",
        finalidad="finalidad test",
        base_legal="Consentimiento",
        fuente_datos="titular",
        plazo_retencion="1 año",
        datos_sensibles=True,
        evaluacion_impacto=True,
        estado=EstadoRAT.BORRADOR,
        estado_eipd=EstadoEIPD.PENDIENTE,
    )
    db.add(rat)
    db.commit()
    db.refresh(rat)
    return rat


class TestSyncRatEstadoEipd:
    """Verifica que rat.estado_eipd se mantenga coherente con eipd.resultado."""

    def test_crear_eipd_en_proceso_sincroniza_rat(self, db, rat_con_sensibles):
        """EIPD con resultado=en_proceso -> rat.estado_eipd = en_proceso."""
        data = EIPDCreate(
            rat_id=rat_con_sensibles.id,
            resultado="en_proceso",
        )
        eipd = crear_eipd(db, data, "test_user")

        db.refresh(rat_con_sensibles)
        assert eipd.resultado == ResultadoEIPD.EN_PROCESO
        assert rat_con_sensibles.estado_eipd == EstadoEIPD.EN_PROCESO

    def test_crear_eipd_completada_sincroniza_rat(self, db, rat_con_sensibles):
        data = EIPDCreate(
            rat_id=rat_con_sensibles.id,
            resultado="completada",
        )
        crear_eipd(db, data, "test_user")

        db.refresh(rat_con_sensibles)
        assert rat_con_sensibles.estado_eipd == EstadoEIPD.COMPLETADA

    def test_crear_eipd_no_requerida_sincroniza_rat(self, db, rat_con_sensibles):
        data = EIPDCreate(
            rat_id=rat_con_sensibles.id,
            resultado="no_requerida",
        )
        crear_eipd(db, data, "test_user")

        db.refresh(rat_con_sensibles)
        assert rat_con_sensibles.estado_eipd == EstadoEIPD.NO_REQUERIDA

    def test_actualizar_eipd_sincroniza_rat(self, db, rat_con_sensibles):
        """Cambiar el resultado de en_proceso a completada actualiza rat.estado_eipd."""
        create_data = EIPDCreate(rat_id=rat_con_sensibles.id, resultado="en_proceso")
        eipd = crear_eipd(db, create_data, "test_user")

        update_data = EIPDUpdate(resultado="completada")
        actualizar_eipd(db, eipd.id, update_data, "test_user")

        db.refresh(rat_con_sensibles)
        db.refresh(eipd)
        assert eipd.resultado == ResultadoEIPD.COMPLETADA
        assert rat_con_sensibles.estado_eipd == EstadoEIPD.COMPLETADA

    def test_rat_empieza_en_pendiente_antes_de_eipd(self, db, rat_con_sensibles):
        """El fixture inicializa rat con estado_eipd=pendiente antes de que exista la EIPD."""
        assert rat_con_sensibles.estado_eipd == EstadoEIPD.PENDIENTE


class TestCrearEipdValidaciones:
    """Verifica validaciones de crear_eipd."""

    def test_eipd_duplicado_falla(self, db, rat_con_sensibles):
        from app.services.eipd_service import EIPDJaExisteError

        crear_eipd(db, EIPDCreate(rat_id=rat_con_sensibles.id, resultado="en_proceso"), "u")

        with pytest.raises(EIPDJaExisteError):
            crear_eipd(db, EIPDCreate(rat_id=rat_con_sensibles.id, resultado="en_proceso"), "u")

    def test_resultado_invalido_falla(self, db, rat_con_sensibles):
        from app.services.eipd_service import ResultadoInvalidoError

        with pytest.raises(ResultadoInvalidoError):
            crear_eipd(db, EIPDCreate(rat_id=rat_con_sensibles.id, resultado="ESTADO_FANTASMA"), "u")

    def test_rat_inexistente_falla(self, db, empresa):
        from app.services.eipd_service import RATNotFoundError

        with pytest.raises(RATNotFoundError):
            crear_eipd(db, EIPDCreate(rat_id=999_999, resultado="en_proceso"), "u")
