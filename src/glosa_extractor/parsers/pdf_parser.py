from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..normalization import normalize_dataframe
from ..schema import ALL_COLUMNS

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None


def _table_to_dataframe(table: list[list[str | None]]) -> pd.DataFrame:
    if not table or len(table) < 2:
        return pd.DataFrame()

    header = ["" if cell is None else str(cell).strip() for cell in table[0]]
    rows = table[1:]
    max_len = max(len(header), *(len(r) for r in rows))
    if max_len == 0:
        return pd.DataFrame()

    if len(header) < max_len:
        header += [f"col_{i}" for i in range(len(header), max_len)]

    normalized_rows = []
    for row in rows:
        values = ["" if cell is None else str(cell).strip() for cell in row]
        if len(values) < max_len:
            values += [""] * (max_len - len(values))
        normalized_rows.append(values[:max_len])

    return pd.DataFrame(normalized_rows, columns=header[:max_len])


def parse_pdf(file_path: Path) -> pd.DataFrame:
    if pdfplumber is None:
        return pd.DataFrame(columns=ALL_COLUMNS)

    frames: list[pd.DataFrame] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables() or []
            for table in tables:
                page_df = _table_to_dataframe(table)
                if page_df.empty:
                    continue
                normalized = normalize_dataframe(page_df, source_file=file_path)
                if not normalized.empty:
                    frames.append(normalized)

    if not frames:
        return pd.DataFrame(columns=ALL_COLUMNS)

    return pd.concat(frames, ignore_index=True)

