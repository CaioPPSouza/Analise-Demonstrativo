from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable

import pandas as pd


DEFAULT_GLOSA_DIR = Path(r"C:\Desenvolvimento\Demonstrativo-Analista\Codigo-Glosas")


def _is_filled(value: object) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    return text != "" and text.lower() != "nan"


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _clean_description(text: str) -> str:
    cleaned = _normalize_spaces(text.strip(" ,;:-"))
    cleaned = re.sub(
        r"^descri(?:ç|c)[aã]o\s+glosa\s*:?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip(" ,;:-")


def _clean_definition(text: str) -> str:
    cleaned = _normalize_spaces(text.strip(" ,;:-"))
    cleaned = re.sub(
        r"^defini(?:ç|c)(?:[aã]o|oes|ões)?(?:\s+da\s+glosa)?\s*[:=]?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip(" ,;:-")


def _parse_catalog_line(line: str) -> tuple[str, str, str] | None:
    text = line.strip()
    if not text:
        return None

    match = re.match(r"^(\d{3,5})\s*=\s*(.+)$", text)
    if not match:
        return None

    code = match.group(1)
    rest = match.group(2).strip()
    rest = re.sub(r"^\s*=\s*", "", rest)
    rest = _normalize_spaces(rest)

    description = ""
    definition = ""

    definition_label = re.search(
        r"defini(?:ç|c)(?:[aã]o|oes|ões)?(?:\s+da\s+glosa)?\s*[:=]",
        rest,
        flags=re.IGNORECASE,
    )
    if definition_label:
        left = rest[: definition_label.start()].strip(" ,;:-")
        right = rest[definition_label.end() :].strip(" ,;:-")
        description = _clean_description(left)
        definition = _clean_definition(right)
        return code, description, definition

    parts = [part.strip(" ,;:-") for part in rest.split("=")]
    non_empty_parts = [part for part in parts if part]
    if len(non_empty_parts) >= 2:
        description = _clean_description(non_empty_parts[0])
        definition = _clean_definition(non_empty_parts[1])
    elif len(non_empty_parts) == 1:
        description = _clean_description(non_empty_parts[0])

    return code, description, definition


def _read_text_fallback(path: Path) -> str:
    for encoding in ("utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def _catalog_dirs() -> list[Path]:
    env_dir = os.getenv("AMIL_GLOSA_CODES_DIR", "").strip()
    repo_root_dir = Path(__file__).resolve().parents[2] / "Codigo-Glosas"
    cwd_dir = Path.cwd() / "Codigo-Glosas"

    dirs: list[Path] = []
    for raw in [env_dir, str(DEFAULT_GLOSA_DIR), str(repo_root_dir), str(cwd_dir)]:
        if not raw:
            continue
        path = Path(raw).expanduser()
        if path.exists() and path.is_dir():
            resolved = path.resolve()
            if resolved not in dirs:
                dirs.append(resolved)
    return dirs


def load_glosa_catalog() -> dict[str, tuple[str, str]]:
    catalog: dict[str, tuple[str, str]] = {}

    for folder in _catalog_dirs():
        for txt_file in sorted(folder.glob("*.txt")):
            try:
                content = _read_text_fallback(txt_file)
            except OSError:
                continue

            for line in content.splitlines():
                parsed = _parse_catalog_line(line)
                if parsed is None:
                    continue
                code, description, definition = parsed
                current_description, current_definition = catalog.get(code, ("", ""))
                catalog[code] = (
                    current_description if current_description else description,
                    current_definition if current_definition else definition,
                )

    return catalog


def _split_codes(raw_value: object) -> list[str]:
    if not _is_filled(raw_value):
        return []
    found = re.findall(r"\d{3,5}", str(raw_value))
    unique: list[str] = []
    for code in found:
        if code not in unique:
            unique.append(code)
    return unique


def _join_unique(values: Iterable[str]) -> str:
    out: list[str] = []
    for value in values:
        text = value.strip()
        if text and text not in out:
            out.append(text)
    return " | ".join(out)


def apply_glosa_catalog_fallback(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe is None or dataframe.empty:
        return dataframe
    if "glosa_codigo" not in dataframe.columns:
        return dataframe

    catalog = load_glosa_catalog()
    if not catalog:
        return dataframe

    frame = dataframe.copy()
    for idx, row in frame.iterrows():
        row_codes = _split_codes(row.get("glosa_codigo"))
        if not row_codes:
            continue

        desc_missing = not _is_filled(row.get("glosa_descricao"))
        def_missing = not _is_filled(row.get("glosa_definicao"))
        if not desc_missing and not def_missing:
            continue

        descriptions = []
        definitions = []
        for code in row_codes:
            if code not in catalog:
                continue
            description, definition = catalog[code]
            if description:
                descriptions.append(description)
            if definition:
                definitions.append(definition)

        if desc_missing and descriptions:
            frame.at[idx, "glosa_descricao"] = _join_unique(descriptions)
        if def_missing and definitions:
            frame.at[idx, "glosa_definicao"] = _join_unique(definitions)

    return frame
