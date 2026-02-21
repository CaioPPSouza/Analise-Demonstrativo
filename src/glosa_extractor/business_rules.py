from __future__ import annotations

from typing import Any


def _is_filled(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return text != "" and text.lower() != "nan"


def is_glosa_row(row: dict[str, Any]) -> bool:
    tipo_glosa = row.get("tipo_glosa")
    valor_glosado = row.get("valor_glosado")
    valor_informado = row.get("valor_informado")
    valor_pago = row.get("valor_pago")

    if _is_filled(tipo_glosa):
        return True

    if isinstance(valor_glosado, (int, float)) and valor_glosado > 0:
        return True

    if isinstance(valor_informado, (int, float)) and isinstance(valor_pago, (int, float)):
        return valor_pago < valor_informado

    return False


def fill_derived_valor_glosado(row: dict[str, Any]) -> float | None:
    valor_glosado = row.get("valor_glosado")
    if isinstance(valor_glosado, (int, float)) and valor_glosado > 0:
        return float(valor_glosado)

    valor_informado = row.get("valor_informado")
    valor_pago = row.get("valor_pago")
    if isinstance(valor_informado, (int, float)) and isinstance(valor_pago, (int, float)):
        diff = valor_informado - valor_pago
        if diff > 0:
            return float(diff)
    return None

