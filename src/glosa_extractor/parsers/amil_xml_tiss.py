from __future__ import annotations

from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import pandas as pd

from ..amil_schema import AMIL_ALL_COLUMNS
from ..normalization import normalize_date, parse_decimal


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    if ":" in tag:
        return tag.rsplit(":", 1)[1]
    return tag


def _clean_text(text: str | None) -> str:
    return "" if text is None else text.strip()


def _find_first_deep(element: ET.Element, tag_names: list[str]) -> str:
    wanted = set(tag_names)
    for node in element.iter():
        if _local_name(node.tag) in wanted:
            value = _clean_text(node.text)
            if value:
                return value
    return ""


def _find_first_shallow(element: ET.Element, tag_names: list[str]) -> str:
    wanted = set(tag_names)
    for node in list(element):
        if _local_name(node.tag) in wanted:
            value = _clean_text(node.text)
            if value:
                return value
    return ""


def _find_all_deep(element: ET.Element, tag_names: list[str]) -> list[str]:
    wanted = set(tag_names)
    values: list[str] = []
    for node in element.iter():
        if _local_name(node.tag) in wanted:
            value = _clean_text(node.text)
            if value:
                values.append(value)
    return values


def _parent_map(root: ET.Element) -> dict[ET.Element, ET.Element]:
    parents: dict[ET.Element, ET.Element] = {}
    for parent in root.iter():
        for child in list(parent):
            parents[child] = parent
    return parents


def _ancestors(node: ET.Element, parents: dict[ET.Element, ET.Element]) -> list[ET.Element]:
    chain: list[ET.Element] = []
    current = node
    while current in parents:
        current = parents[current]
        chain.append(current)
    return chain


def _extract_from_context(
    context: ET.Element,
    ancestors: list[ET.Element],
    root: ET.Element,
    tag_names: list[str],
) -> str:
    value = _find_first_deep(context, tag_names)
    if value:
        return value

    for ancestor in ancestors:
        value = _find_first_shallow(ancestor, tag_names)
        if value:
            return value

    return _find_first_deep(root, tag_names)


def _unique_non_empty(values: list[str]) -> list[str]:
    out: list[str] = []
    for value in values:
        text = value.strip()
        if text and text not in out:
            out.append(text)
    return out


def _join_unique(values: list[str]) -> str:
    unique = _unique_non_empty(values)
    return " | ".join(unique)


def _compute_valor_glosa(guia: ET.Element) -> float | None:
    valor_guia = parse_decimal(_find_first_deep(guia, ["valorGlosaGuia"]))
    if isinstance(valor_guia, float) and valor_guia > 0:
        return valor_guia

    valores_relacao = [parse_decimal(v) for v in _find_all_deep(guia, ["valorGlosa"])]
    valores_relacao = [v for v in valores_relacao if isinstance(v, float) and v > 0]
    if valores_relacao:
        return float(sum(valores_relacao))

    valor_informado = parse_decimal(_find_first_deep(guia, ["valorInformadoGuia", "valorInformado"]))
    valor_liberado = parse_decimal(_find_first_deep(guia, ["valorLiberadoGuia", "valorLiberado"]))
    if isinstance(valor_informado, float) and isinstance(valor_liberado, float):
        diff = valor_informado - valor_liberado
        if diff > 0:
            return float(diff)
    return None


def parse_xml_tiss_amil(file_path: Path) -> pd.DataFrame:
    root = ET.parse(file_path).getroot()
    parents = _parent_map(root)

    guia_nodes = [node for node in root.iter() if _local_name(node.tag) == "relacaoGuias"]
    rows: list[dict[str, Any]] = []

    for guia in guia_nodes:
        anc = _ancestors(guia, parents)

        glosa_codigos = _find_all_deep(guia, ["codigoGlosa", "tipoGlosa"])
        glosa_descricoes = _find_all_deep(guia, ["descricaoGlosa", "descricaoMotivoGlosa"])

        row = {col: "" for col in AMIL_ALL_COLUMNS}
        row["arquivo_origem"] = file_path.name
        row["protocolo_numero"] = _extract_from_context(guia, anc, root, ["numeroProtocolo"])
        row["numero_lote"] = _extract_from_context(guia, anc, root, ["numeroLotePrestador", "numeroLote"])
        row["beneficiario_nome"] = _extract_from_context(
            guia,
            anc,
            root,
            [
                "nomeBeneficiario",
                "nomeBeneficiário",
                "nomeUsuario",
                "nomeSegurado",
                "nomePaciente",
                "nomeTitular",
            ],
        )
        row["beneficiario_codigo"] = _extract_from_context(
            guia,
            anc,
            root,
            ["numeroCarteira", "codigoBeneficiario", "codigoUsuarioBeneficiario"],
        )
        row["guia_prestador_numero"] = _extract_from_context(guia, anc, root, ["numeroGuiaPrestador"])
        row["guia_operadora_numero"] = _extract_from_context(guia, anc, root, ["numeroGuiaOperadora"])
        row["data_realizacao"] = normalize_date(
            _extract_from_context(guia, anc, root, ["dataRealizacao", "dataInicioFat", "dataAtendimento"])
        )
        row["glosa_codigo"] = _join_unique(glosa_codigos)
        row["glosa_descricao"] = _join_unique(glosa_descricoes)
        row["valor_glosa"] = _compute_valor_glosa(guia)
        rows.append(row)

    if not rows:
        return pd.DataFrame(columns=AMIL_ALL_COLUMNS)
    return pd.DataFrame(rows, columns=AMIL_ALL_COLUMNS)
