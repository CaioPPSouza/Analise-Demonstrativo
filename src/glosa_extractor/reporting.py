from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .business_rules import fill_derived_valor_glosado, is_glosa_row
from .parsers.pdf_parser import parse_pdf
from .parsers.xlsx_parser import parse_xlsx
from .parsers.xml_tiss import parse_xml_tiss
from .schema import ALL_COLUMNS, EXPORT_COLUMNS, EXPORT_HEADERS

SUPPORTED_EXTENSIONS = {".xml", ".xlsx", ".xls", ".pdf"}


@dataclass
class ParsedResult:
    dataframe: pd.DataFrame
    warnings: list[str]


def discover_input_files(paths: Iterable[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)
            continue
        if path.is_dir():
            for file in path.rglob("*"):
                if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS:
                    files.append(file)

    unique: dict[str, Path] = {}
    for file in files:
        unique[str(file.resolve())] = file
    return list(unique.values())


def parse_file(file_path: Path) -> pd.DataFrame:
    ext = file_path.suffix.lower()
    if ext == ".xml":
        return parse_xml_tiss(file_path)
    if ext in {".xlsx", ".xls"}:
        return parse_xlsx(file_path)
    if ext == ".pdf":
        return parse_pdf(file_path)
    return pd.DataFrame(columns=ALL_COLUMNS)


def parse_inputs(paths: Iterable[Path]) -> ParsedResult:
    files = discover_input_files(paths)
    warnings: list[str] = []
    frames: list[pd.DataFrame] = []

    for file in files:
        try:
            frame = parse_file(file)
        except Exception as exc:  # pragma: no cover
            warnings.append(f"Falha ao processar {file.name}: {exc}")
            continue
        if frame is not None and not frame.empty:
            frames.append(frame)

    if not frames:
        return ParsedResult(dataframe=pd.DataFrame(columns=ALL_COLUMNS), warnings=warnings)

    merged = pd.concat(frames, ignore_index=True)
    merged = merged.reindex(columns=ALL_COLUMNS)
    return ParsedResult(dataframe=merged, warnings=warnings)


def filter_glosa_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return pd.DataFrame(columns=ALL_COLUMNS)

    records = dataframe.to_dict(orient="records")
    filtered_records: list[dict[str, Any]] = []
    for record in records:
        derived = fill_derived_valor_glosado(record)
        if derived is not None:
            record["valor_glosado"] = derived
        if is_glosa_row(record):
            filtered_records.append(record)

    if not filtered_records:
        return pd.DataFrame(columns=ALL_COLUMNS)

    glosa_df = pd.DataFrame(filtered_records)
    return glosa_df.reindex(columns=ALL_COLUMNS)


def output_columns_dataframe(glosa_df: pd.DataFrame) -> pd.DataFrame:
    if glosa_df is None or glosa_df.empty:
        return pd.DataFrame(columns=list(EXPORT_HEADERS.values()))
    export_df = glosa_df.reindex(columns=EXPORT_COLUMNS)
    return export_df.rename(columns=EXPORT_HEADERS)


def _unique_non_empty(values: pd.Series) -> list[str]:
    out: list[str] = []
    for value in values:
        text = "" if value is None else str(value).strip()
        if text and text.lower() != "nan" and text not in out:
            out.append(text)
    return out


def summarize_single_or_multiple(values: pd.Series) -> str:
    unique = _unique_non_empty(values)
    if not unique:
        return "-"
    if len(unique) == 1:
        return unique[0]
    return f"Multiplos ({len(unique)})"


def detect_demonstrativo_tipo(dataframe: pd.DataFrame) -> str:
    if dataframe is None or dataframe.empty:
        return "desconhecido"

    if "tipo_demonstrativo" in dataframe.columns:
        tipos = _unique_non_empty(dataframe["tipo_demonstrativo"])
        tipos_norm = {tipo.strip().lower() for tipo in tipos}
        if "pagamento" in tipos_norm and "contas_medicas" not in tipos_norm:
            return "pagamento"
        if "contas_medicas" in tipos_norm and "pagamento" not in tipos_norm:
            return "contas_medicas"
        if len(tipos_norm) == 1:
            return next(iter(tipos_norm))

    detail_cols = ["guia_prestador", "codigo_procedimento", "descricao_procedimento", "data_realizacao"]
    for col in detail_cols:
        if col in dataframe.columns:
            if any(text for text in _unique_non_empty(dataframe[col]) if text != "-"):
                return "contas_medicas"

    total_cols = ["valor_informado_total", "valor_glosado_total", "valor_pago_total"]
    for col in total_cols:
        if col in dataframe.columns:
            if pd.to_numeric(dataframe[col], errors="coerce").notna().any():
                return "pagamento"

    return "desconhecido"


def _sum_deduplicated_total(dataframe: pd.DataFrame, total_col: str) -> float | None:
    if dataframe is None or dataframe.empty or total_col not in dataframe.columns:
        return None

    temp = dataframe.copy()
    temp[total_col] = pd.to_numeric(temp[total_col], errors="coerce")
    temp = temp[temp[total_col].notna()]
    if temp.empty:
        return None

    key_candidates = ["arquivo_origem", "protocolo_numero", "numero_lote", "ans_operadora"]
    key_cols = [col for col in key_candidates if col in temp.columns]
    if key_cols:
        grouped = temp.groupby(key_cols, dropna=False)[total_col].max()
        return float(grouped.sum())
    return float(temp[total_col].max())


def summarize_demonstrativo(dataframe: pd.DataFrame, glosa_df: pd.DataFrame) -> dict[str, Any]:
    if dataframe is None or dataframe.empty:
        return {
            "tipo_demonstrativo": "desconhecido",
            "numero_lote": "-",
            "protocolo_numero": "-",
            "ans_operadora": "-",
            "valor_total_faturado": 0.0,
            "valor_total_glosado": 0.0,
            "quantidade_guias_glosadas": 0,
        }

    tipo_demonstrativo = detect_demonstrativo_tipo(dataframe)

    # Regra de negocio:
    # - pagamento: total consolidado de todos os protocolos do demonstrativo.
    # - contas medicas: usar total informado/glosado do protocolo quando disponivel.
    if tipo_demonstrativo == "pagamento":
        valor_total_faturado = _sum_deduplicated_total(dataframe, "valor_informado_total")
        valor_total_glosado = _sum_deduplicated_total(dataframe, "valor_glosado_total")
    elif tipo_demonstrativo == "contas_medicas":
        valor_total_faturado = _sum_deduplicated_total(dataframe, "valor_informado_total")
        valor_total_glosado = _sum_deduplicated_total(dataframe, "valor_glosado_total")
    else:
        valor_total_faturado = None
        valor_total_glosado = None

    if valor_total_faturado is None:
        valor_informado = pd.to_numeric(dataframe["valor_informado"], errors="coerce")
        valor_pago = pd.to_numeric(dataframe["valor_pago"], errors="coerce")
        valor_glosado_base = pd.to_numeric(dataframe["valor_glosado"], errors="coerce")

        valor_total_faturado_series = valor_informado.copy()
        missing_informado = valor_total_faturado_series.isna()
        valor_total_faturado_series.loc[missing_informado] = (
            valor_pago.fillna(0) + valor_glosado_base.fillna(0)
        ).loc[missing_informado]
        valor_total_faturado = float(valor_total_faturado_series.fillna(0).sum())

    quantidade_guias_glosadas = 0

    if valor_total_glosado is None:
        if glosa_df is not None and not glosa_df.empty:
            valor_total_glosado = float(
                pd.to_numeric(glosa_df["valor_glosado"], errors="coerce").fillna(0).sum()
            )
        else:
            valor_total_glosado = 0.0

    if glosa_df is not None and not glosa_df.empty:
        guia_keys = glosa_df["guia_prestador"].fillna("").astype(str).str.strip()
        operadora_keys = glosa_df["numero_guia_operadora"].fillna("").astype(str).str.strip()
        merged_keys = []
        for guia, operadora in zip(guia_keys, operadora_keys):
            key = guia if guia else operadora
            if key:
                merged_keys.append(key)
        if merged_keys:
            quantidade_guias_glosadas = len(set(merged_keys))
        else:
            quantidade_guias_glosadas = len(glosa_df)

    return {
        "tipo_demonstrativo": tipo_demonstrativo,
        "numero_lote": summarize_single_or_multiple(dataframe["numero_lote"]),
        "protocolo_numero": summarize_single_or_multiple(dataframe["protocolo_numero"]),
        "ans_operadora": summarize_single_or_multiple(dataframe["ans_operadora"]),
        "valor_total_faturado": float(valor_total_faturado),
        "valor_total_glosado": float(valor_total_glosado),
        "quantidade_guias_glosadas": int(quantidade_guias_glosadas),
    }
