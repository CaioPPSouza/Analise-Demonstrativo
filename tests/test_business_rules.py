from glosa_extractor.business_rules import fill_derived_valor_glosado, is_glosa_row


def test_is_glosa_row_by_tipo_glosa():
    row = {"tipo_glosa": "701", "valor_glosado": None, "valor_informado": None, "valor_pago": None}
    assert is_glosa_row(row) is True


def test_is_glosa_row_by_valor_glosado():
    row = {"tipo_glosa": "", "valor_glosado": 10.0, "valor_informado": None, "valor_pago": None}
    assert is_glosa_row(row) is True


def test_is_glosa_row_by_valor_pago_menor():
    row = {"tipo_glosa": "", "valor_glosado": None, "valor_informado": 100.0, "valor_pago": 60.0}
    assert is_glosa_row(row) is True


def test_is_glosa_row_false_when_pago_integral():
    row = {"tipo_glosa": "", "valor_glosado": None, "valor_informado": 100.0, "valor_pago": 100.0}
    assert is_glosa_row(row) is False


def test_fill_derived_valor_glosado():
    row = {"valor_glosado": None, "valor_informado": 250.0, "valor_pago": 200.0}
    assert fill_derived_valor_glosado(row) == 50.0

