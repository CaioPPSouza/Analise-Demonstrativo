from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from .parsers.amil_xml_tiss import parse_xml_tiss_amil
from .amil_normalization import normalize_dataframe
from .amil_schema import AMIL_ALL_COLUMNS, AMIL_EXPORT_COLUMNS, AMIL_EXPORT_HEADERS

SUPPORTED_EXTENSIONS = {".xml", ".xlsx", ".xls", ".pdf"}

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None


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


def _parse_xlsx(file_path: Path) -> pd.DataFrame:
    workbook = pd.read_excel(file_path, sheet_name=None)
    frames: list[pd.DataFrame] = []

    for _, sheet_df in workbook.items():
        if sheet_df is None or sheet_df.empty:
            continue
        normalized = normalize_dataframe(sheet_df, source_file=file_path)
        if not normalized.empty:
            frames.append(normalized)

    if not frames:
        return pd.DataFrame(columns=AMIL_ALL_COLUMNS)
    return pd.concat(frames, ignore_index=True)


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


def _parse_pdf(file_path: Path) -> pd.DataFrame:
    if pdfplumber is None:
        return pd.DataFrame(columns=AMIL_ALL_COLUMNS)

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
        return pd.DataFrame(columns=AMIL_ALL_COLUMNS)
    return pd.concat(frames, ignore_index=True)


def parse_file(file_path: Path) -> pd.DataFrame:
    ext = file_path.suffix.lower()
    if ext == ".xml":
        return parse_xml_tiss_amil(file_path)
    if ext in {".xlsx", ".xls"}:
        return _parse_xlsx(file_path)
    if ext == ".pdf":
        return _parse_pdf(file_path)
    return pd.DataFrame(columns=AMIL_ALL_COLUMNS)


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
        return ParsedResult(dataframe=pd.DataFrame(columns=AMIL_ALL_COLUMNS), warnings=warnings)

    merged = pd.concat(frames, ignore_index=True)
    merged = merged.reindex(columns=AMIL_ALL_COLUMNS)
    return ParsedResult(dataframe=merged, warnings=warnings)


def _is_filled(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return text != "" and text.lower() != "nan"


def _has_identity_fields(record: dict[str, Any]) -> bool:
    identity_fields = (
        "protocolo_numero",
        "numero_lote",
        "beneficiario_nome",
        "beneficiario_codigo",
        "guia_prestador_numero",
        "guia_operadora_numero",
    )
    return any(_is_filled(record.get(field)) for field in identity_fields)


def filter_glosa_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return pd.DataFrame(columns=AMIL_ALL_COLUMNS)

    records = dataframe.to_dict(orient="records")
    filtered_records: list[dict[str, Any]] = []
    for record in records:
        if not _has_identity_fields(record):
            continue

        valor_glosa = record.get("valor_glosa")
        if isinstance(valor_glosa, (int, float)) and valor_glosa > 0:
            filtered_records.append(record)
            continue

        if any(
            _is_filled(record.get(field))
            for field in ("glosa_codigo", "glosa_descricao")
        ):
            filtered_records.append(record)

    if not filtered_records:
        return pd.DataFrame(columns=AMIL_ALL_COLUMNS)

    glosa_df = pd.DataFrame(filtered_records)
    return glosa_df.reindex(columns=AMIL_ALL_COLUMNS)


def output_columns_dataframe(glosa_df: pd.DataFrame) -> pd.DataFrame:
    if glosa_df is None or glosa_df.empty:
        return pd.DataFrame(columns=list(AMIL_EXPORT_HEADERS.values()))
    export_df = glosa_df.reindex(columns=AMIL_EXPORT_COLUMNS)
    return export_df.rename(columns=AMIL_EXPORT_HEADERS)


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
    return f"Múltiplos ({len(unique)})"


def summarize_demonstrativo(dataframe: pd.DataFrame, glosa_df: pd.DataFrame) -> dict[str, Any]:
    if dataframe is None or dataframe.empty:
        return {
            "tipo_demonstrativo": "amil",
            "numero_lote": "-",
            "protocolo_numero": "-",
            "valor_total_glosado": 0.0,
            "quantidade_guias_glosadas": 0,
        }

    quantidade_guias_glosadas = 0
    valor_total_glosado = 0.0
    if glosa_df is not None and not glosa_df.empty:
        valor_total_glosado = float(pd.to_numeric(glosa_df["valor_glosa"], errors="coerce").fillna(0).sum())

        guia_prestador = glosa_df["guia_prestador_numero"].fillna("").astype(str).str.strip()
        guia_operadora = glosa_df["guia_operadora_numero"].fillna("").astype(str).str.strip()
        merged_keys = []
        for prestador, operadora in zip(guia_prestador, guia_operadora):
            key = prestador if prestador else operadora
            if key:
                merged_keys.append(key)
        quantidade_guias_glosadas = len(set(merged_keys)) if merged_keys else len(glosa_df)

    return {
        "tipo_demonstrativo": "amil",
        "numero_lote": summarize_single_or_multiple(dataframe["numero_lote"]),
        "protocolo_numero": summarize_single_or_multiple(dataframe["protocolo_numero"]),
        "valor_total_glosado": float(valor_total_glosado),
        "quantidade_guias_glosadas": int(quantidade_guias_glosadas),
    }
