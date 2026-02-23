from __future__ import annotations

import math
import re
import unicodedata
from pathlib import Path
from typing import Any

import pandas as pd

from .amil_schema import AMIL_ALL_COLUMNS, AMIL_CANONICAL_COLUMNS, AMIL_HEADER_ALIASES
from .normalization import normalize_date, parse_decimal


def _to_clean_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        if value.is_integer():
            return str(int(value))
    return str(value).strip()


def normalize_header(name: Any) -> str:
    if name is None:
        return ""

    text = str(name).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def map_headers(columns: list[Any]) -> dict[Any, str]:
    mapped: dict[Any, str] = {}
    for original in columns:
        normalized = normalize_header(original)
        canonical_match = None
        for canonical, aliases in AMIL_HEADER_ALIASES.items():
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
        return pd.DataFrame(columns=AMIL_ALL_COLUMNS)

    frame = df.copy()
    frame.columns = [str(c) for c in frame.columns]
    header_map = map_headers(list(frame.columns))
    frame = frame.rename(columns=header_map)

    for col in AMIL_ALL_COLUMNS:
        if col not in frame.columns:
            frame[col] = None

    frame["arquivo_origem"] = source_file.name
    frame["data_realizacao"] = frame["data_realizacao"].map(normalize_date)
    frame["valor_glosa"] = frame["valor_glosa"].map(parse_decimal)

    for col in AMIL_CANONICAL_COLUMNS:
        if col not in {"data_realizacao", "valor_glosa"}:
            frame[col] = frame[col].map(_to_clean_text)

    return frame[AMIL_ALL_COLUMNS]
