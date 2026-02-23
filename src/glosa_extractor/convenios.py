from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol

import pandas as pd

from . import amil_reporting, reporting

DEFAULT_CONVENIO = "bradesco"


class ParseResultLike(Protocol):
    dataframe: pd.DataFrame
    warnings: list[str]


@dataclass(frozen=True)
class ConvenioConfig:
    key: str
    label: str
    parse_inputs: Callable[[Iterable[Path]], ParseResultLike]
    filter_glosa_rows: Callable[[pd.DataFrame], pd.DataFrame]
    output_columns_dataframe: Callable[[pd.DataFrame], pd.DataFrame]
    summarize_demonstrativo: Callable[[pd.DataFrame, pd.DataFrame], dict[str, Any]]


CONVENIOS: dict[str, ConvenioConfig] = {
    "bradesco": ConvenioConfig(
        key="bradesco",
        label="Bradesco",
        parse_inputs=reporting.parse_inputs,
        filter_glosa_rows=reporting.filter_glosa_rows,
        output_columns_dataframe=reporting.output_columns_dataframe,
        summarize_demonstrativo=reporting.summarize_demonstrativo,
    ),
    "amil": ConvenioConfig(
        key="amil",
        label="AMIL",
        parse_inputs=amil_reporting.parse_inputs,
        filter_glosa_rows=amil_reporting.filter_glosa_rows,
        output_columns_dataframe=amil_reporting.output_columns_dataframe,
        summarize_demonstrativo=amil_reporting.summarize_demonstrativo,
    ),
}


def list_convenios() -> list[ConvenioConfig]:
    return [CONVENIOS["bradesco"], CONVENIOS["amil"]]


def get_convenio_config(convenio: str | None) -> ConvenioConfig:
    key = DEFAULT_CONVENIO if convenio is None else convenio.strip().lower()
    if key not in CONVENIOS:
        valid = ", ".join(sorted(CONVENIOS))
        raise ValueError(f"Convênio inválido '{convenio}'. Opções: {valid}.")
    return CONVENIOS[key]
