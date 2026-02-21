from __future__ import annotations

from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

import pandas as pd

from ..normalization import normalize_date, parse_decimal
from ..schema import ALL_COLUMNS


FIELD_TAGS = {
    "ans_operadora": ["registroANS"],
    "numero_lote": ["numeroLote", "numeroLotePrestador"],
    "prestador_numero": ["codigoPrestadorNaOperadora", "nomeContratado"],
    "protocolo_numero": ["numeroProtocolo"],
    "guia_prestador": ["numeroGuiaPrestador"],
    "senha": ["senha", "senhaAutorizacao"],
    "numero_guia_operadora": ["numeroGuiaOperadora"],
    "data_realizacao": ["dataRealizacao", "dataAtendimento", "dataExecucao", "dataProcedimento"],
    "codigo_procedimento": ["codigoProcedimento"],
    "descricao_procedimento": ["descricaoProcedimento", "descricao"],
    "tipo_glosa": ["codigoGlosa", "tipoGlosa", "descricaoGlosa", "motivoGlosa"],
    "valor_glosado": ["valorGlosa"],
    "valor_informado": ["valorInformado", "valorCobrado"],
    "valor_pago": ["valorPago", "valorPagoIntegral", "valorPagoProcedimento", "valorLiberado"],
}

TOTAL_TAGS = {
    "valor_informado_total": [
        "valorInformadoProtocolo",
        "valorInformadoGeral",
        "valorTotalApresentado",
        "valorTotalFaturado",
        "valorApresentado",
    ],
    "valor_pago_total": [
        "valorLiberadoProtocolo",
        "valorLiberadoGeral",
        "valorTotalLiberado",
        "valorTotalPago",
        "valorPagoTotal",
        "valorProcessadoProtocolo",
        "valorProcessadoGeral",
    ],
    "valor_glosado_total": [
        "valorGlosaProtocolo",
        "valorGlosaGeral",
        "valorTotalGlosa",
    ],
}


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


def _global_values(root: ET.Element) -> dict[str, str]:
    return {
        "ans_operadora": _find_first_deep(root, FIELD_TAGS["ans_operadora"]),
        "numero_lote": _find_first_deep(root, FIELD_TAGS["numero_lote"]),
        "prestador_numero": _find_first_deep(root, FIELD_TAGS["prestador_numero"]),
    }


def _detect_demonstrativo_type(root: ET.Element) -> str:
    names = {_local_name(node.tag) for node in root.iter()}
    lowered = {name.lower() for name in names}

    if "demonstrativopagamento" in lowered:
        return "pagamento"
    if "demonstrativoanaliseconta" in lowered or "dadosconta" in lowered:
        return "contas_medicas"
    if any("demonstrativo" in name and "pagamento" in name for name in lowered):
        return "pagamento"
    if any("glosa" in name for name in lowered):
        return "contas_medicas"
    return "desconhecido"


def _global_totals(root: ET.Element) -> dict[str, float | None]:
    totals: dict[str, float | None] = {}
    for field, tags in TOTAL_TAGS.items():
        totals[field] = parse_decimal(_find_first_deep(root, tags))
    return totals


def parse_xml_tiss(file_path: Path) -> pd.DataFrame:
    root = ET.parse(file_path).getroot()
    parents = _parent_map(root)
    globals_data = _global_values(root)
    totals_data = _global_totals(root)
    tipo_demonstrativo = _detect_demonstrativo_type(root)

    candidate_contexts: dict[int, ET.Element] = {}
    procedure_contexts: dict[int, ET.Element] = {}
    for node in root.iter():
        if _local_name(node.tag) == "codigoProcedimento":
            context = parents.get(node, node)
            procedure_contexts[id(context)] = context

    if procedure_contexts:
        candidate_contexts = procedure_contexts
    else:
        fallback_tags = {"codigoGlosa", "tipoGlosa", "valorGlosa"}
        for node in root.iter():
            if _local_name(node.tag) in fallback_tags:
                context = parents.get(node, node)
                candidate_contexts[id(context)] = context

    rows: list[dict[str, Any]] = []
    for context in candidate_contexts.values():
        anc = _ancestors(context, parents)
        row = {col: "" for col in ALL_COLUMNS}
        row.update(globals_data)
        row["arquivo_origem"] = file_path.name
        row["tipo_demonstrativo"] = tipo_demonstrativo
        row.update(totals_data)

        for field, tags in FIELD_TAGS.items():
            if field in globals_data and globals_data[field]:
                continue
            row[field] = _extract_from_context(context, anc, root, tags)

        row["data_realizacao"] = normalize_date(row["data_realizacao"])
        row["valor_glosado"] = parse_decimal(row["valor_glosado"])
        row["valor_informado"] = parse_decimal(row["valor_informado"])
        row["valor_pago"] = parse_decimal(row["valor_pago"])
        rows.append(row)

    if not rows:
        row = {col: "" for col in ALL_COLUMNS}
        row.update(globals_data)
        row["protocolo_numero"] = _find_first_deep(root, FIELD_TAGS["protocolo_numero"])
        row["arquivo_origem"] = file_path.name
        row["tipo_demonstrativo"] = tipo_demonstrativo
        row.update(totals_data)
        row["valor_informado"] = totals_data.get("valor_informado_total")
        row["valor_pago"] = totals_data.get("valor_pago_total")
        row["valor_glosado"] = totals_data.get("valor_glosado_total")
        rows.append(row)

    return pd.DataFrame(rows, columns=ALL_COLUMNS)
