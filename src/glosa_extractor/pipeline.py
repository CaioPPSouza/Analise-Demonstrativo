from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .convenios import DEFAULT_CONVENIO, get_convenio_config


@dataclass
class ProcessResult:
    dataframe: pd.DataFrame
    warnings: list[str]
    summary: dict[str, Any]
    convenio: str


def process_inputs(paths: Iterable[Path], convenio: str = DEFAULT_CONVENIO) -> ProcessResult:
    config = get_convenio_config(convenio)
    parsed = config.parse_inputs(paths)
    glosa_df = config.filter_glosa_rows(parsed.dataframe)
    output_df = config.output_columns_dataframe(glosa_df)
    summary = config.summarize_demonstrativo(parsed.dataframe, glosa_df)

    if parsed.dataframe.empty:
        return ProcessResult(dataframe=output_df, warnings=parsed.warnings, summary=summary, convenio=config.key)
    return ProcessResult(dataframe=output_df, warnings=parsed.warnings, summary=summary, convenio=config.key)
