from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

from .reporting import filter_glosa_rows, output_columns_dataframe, parse_inputs
from .schema import EXPORT_HEADERS


@dataclass
class ProcessResult:
    dataframe: pd.DataFrame
    warnings: list[str]


def process_inputs(paths: Iterable[Path]) -> ProcessResult:
    parsed = parse_inputs(paths)
    if parsed.dataframe.empty:
        return ProcessResult(
            dataframe=pd.DataFrame(columns=list(EXPORT_HEADERS.values())),
            warnings=parsed.warnings,
        )

    glosa_df = filter_glosa_rows(parsed.dataframe)
    output_df = output_columns_dataframe(glosa_df)
    return ProcessResult(dataframe=output_df, warnings=parsed.warnings)
