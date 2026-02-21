from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..normalization import normalize_dataframe
from ..schema import ALL_COLUMNS


def parse_xlsx(file_path: Path) -> pd.DataFrame:
    workbook = pd.read_excel(file_path, sheet_name=None)
    frames: list[pd.DataFrame] = []

    for _, sheet_df in workbook.items():
        if sheet_df is None or sheet_df.empty:
            continue
        normalized = normalize_dataframe(sheet_df, source_file=file_path)
        if not normalized.empty:
            frames.append(normalized)

    if not frames:
        return pd.DataFrame(columns=ALL_COLUMNS)

    return pd.concat(frames, ignore_index=True)

