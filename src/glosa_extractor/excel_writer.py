from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Iterable

import pandas as pd

BRL_NUMBER_FORMAT = 'R$ #,##0.00'


def _apply_currency_format(
    dataframe: pd.DataFrame,
    worksheet,
    currency_columns: Iterable[str] = ("valor_glosado", "Valor Glosado"),
) -> None:
    for col_name in currency_columns:
        if col_name not in dataframe.columns:
            continue
        col_idx = dataframe.columns.get_loc(col_name) + 1
        for row_idx in range(2, len(dataframe) + 2):
            cell = worksheet.cell(row=row_idx, column=col_idx)
            if isinstance(cell.value, (int, float)):
                cell.number_format = BRL_NUMBER_FORMAT


def write_dataframe_to_excel(dataframe: pd.DataFrame, output_path: Path) -> None:
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="glosas")
        worksheet = writer.book["glosas"]
        _apply_currency_format(dataframe, worksheet)


def dataframe_to_excel_bytes(dataframe: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, sheet_name="glosas")
        worksheet = writer.book["glosas"]
        _apply_currency_format(dataframe, worksheet)
    return buffer.getvalue()
