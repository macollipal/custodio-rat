"""Test unitario: verifica que el schema permite no_requerida_justificada"""
from app.schemas.rat import RATBase, RATOut, RATCreate


def test_estado_eipd_acepta_no_requerida_justificada():
    """Test fix: schema debe aceptar no_requerida_justificada."""
    r = RATBase(
        nombre_proceso="Test",
        categoria_datos="X",
        finalidad="Y",
        base_legal="Consentimiento",
        fuente_datos="Web",
        plazo_retencion="5 anos",
        estado_eipd="no_requerida_justificada",
    )
    assert r.estado_eipd == "no_requerida_justificada"
    print("OK: acepta no_requerida_justificada")


def test_estado_eipd_rechaza_valor_invalido():
    """Test: schema debe rechazar valores invalidos."""
    try:
        r = RATBase(
            nombre_proceso="Test",
            categoria_datos="X",
            finalidad="Y",
            base_legal="Consentimiento",
            fuente_datos="Web",
            plazo_retencion="5 anos",
            estado_eipd="valor_invalido",
        )
        assert False, "Debio haber fallado"
    except Exception as e:
        assert "estado_eipd" in str(e)
        print("OK: rechaza valor invalido")


def test_rat_out_valida_con_no_requerida_justificada():
    """Test: RATOut (usado en GET /rats/) debe aceptar el valor."""
    from datetime import datetime
    r = RATOut(
        id=1,
        company_id=1,
        nombre_proceso="Test",
        categoria_datos="X",
        finalidad="Y",
        base_legal="Consentimiento",
        fuente_datos="Web",
        plazo_retencion="5 anos",
        estado_eipd="no_requerida_justificada",
        estado="borrador",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert r.estado_eipd == "no_requerida_justificada"
    print("OK: RATOut acepta no_requerida_justificada")


if __name__ == "__main__":
    test_estado_eipd_acepta_no_requerida_justificada()
    test_estado_eipd_rechaza_valor_invalido()
    test_rat_out_valida_con_no_requerida_justificada()
    print("\nTodos los tests pasaron!")