from __future__ import annotations

import math
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from .schema import ALL_COLUMNS, CANONICAL_COLUMNS, HEADER_ALIASES


def normalize_header(name: Any) -> str:
    if name is None:
        return ""
    text = str(name).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_decimal(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)

    text = str(value).strip()
    if text == "":
        return None
    text = re.sub(r"[R$\s]", "", text)
    text = re.sub(r"[^0-9,.-]", "", text)
    if text in {"", "-", ".", ",", "-.", "-,"}:
        return None

    if text.count(".") > 1 and "," not in text:
        # Ex.: 1.234.567
        text = text.replace(".", "")
    elif text.count(",") > 1 and "." not in text:
        # Ex.: 1,234,567
        text = text.replace(",", "")
    elif "," in text or "." in text:
        # Detecta separador decimal pelo ultimo separador encontrado.
        last_dot = text.rfind(".")
        last_comma = text.rfind(",")
        decimal_sep = "." if last_dot > last_comma else ","
        pos = text.rfind(decimal_sep)
        int_part = re.sub(r"[.,]", "", text[:pos])
        frac_part = re.sub(r"[.,]", "", text[pos + 1 :])

        # Caso comum de milhar sem casas decimais: 1.234 ou 1,234.
        if frac_part and len(frac_part) == 3 and text.count(decimal_sep) == 1:
            text = f"{int_part}{frac_part}"
        else:
            text = f"{int_part}.{frac_part}" if frac_part else int_part

    if text in {"", "-", ".", "-."}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def normalize_date(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y")
    text = str(value).strip()
    if text == "":
        return ""

    patterns = [
        ("%d/%m/%Y", False),
        ("%d-%m-%Y", False),
        ("%Y-%m-%d", False),
        ("%Y/%m/%d", False),
        ("%d/%m/%y", False),
    ]
    for pattern, _ in patterns:
        try:
            return datetime.strptime(text, pattern).strftime("%d-%m-%Y")
        except ValueError:
            pass
    return text


def map_headers(columns: list[Any]) -> dict[Any, str]:
    mapped: dict[Any, str] = {}
    for original in columns:
        normalized = normalize_header(original)
        canonical_match = None
        for canonical, aliases in HEADER_ALIASES.items():
            if normalized in aliases:
                canonical_match = canonical
                break
        if canonical_match:
            mapped[original] = canonical_match
        else:
            mapped[original] = normalized.replace(" ", "_")
    return mapped


def normalize_dataframe(df: pd.DataFrame, source_file: Path) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=ALL_COLUMNS)

    frame = df.copy()
    frame.columns = [str(c) for c in frame.columns]
    header_map = map_headers(list(frame.columns))
    frame = frame.rename(columns=header_map)

    for col in ALL_COLUMNS:
        if col not in frame.columns:
            frame[col] = None

    frame["arquivo_origem"] = source_file.name
    frame["data_realizacao"] = frame["data_realizacao"].map(normalize_date)
    frame["valor_glosado"] = frame["valor_glosado"].map(parse_decimal)
    frame["valor_informado"] = frame["valor_informado"].map(parse_decimal)
    frame["valor_pago"] = frame["valor_pago"].map(parse_decimal)
    frame["valor_informado_total"] = frame["valor_informado_total"].map(parse_decimal)
    frame["valor_pago_total"] = frame["valor_pago_total"].map(parse_decimal)
    frame["valor_glosado_total"] = frame["valor_glosado_total"].map(parse_decimal)
    frame["tipo_demonstrativo"] = frame["tipo_demonstrativo"].map(
        lambda x: "" if x is None else str(x).strip()
    )

    for col in CANONICAL_COLUMNS:
        if col not in {"valor_glosado", "data_realizacao"}:
            frame[col] = frame[col].map(lambda x: "" if x is None else str(x).strip())

    return frame[ALL_COLUMNS]
