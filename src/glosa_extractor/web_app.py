from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from glosa_extractor.excel_writer import dataframe_to_excel_bytes
from glosa_extractor.reporting import (
    filter_glosa_rows,
    output_columns_dataframe,
    parse_inputs,
    summarize_demonstrativo,
)


def _format_currency_brl(value: float) -> str:
    text = f"{value:,.2f}"
    return "R$ " + text.replace(",", "X").replace(".", ",").replace("X", ".")


def _save_uploaded_files(uploaded_files: list[Any]) -> list[Path]:
    base_dir = Path(".tmp_uploads")
    base_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: list[Path] = []
    for uploaded in uploaded_files:
        suffix = Path(uploaded.name).suffix.lower()
        safe_name = Path(uploaded.name).name
        target = base_dir / f"{uuid4().hex}_{safe_name}"
        target.write_bytes(uploaded.getvalue())
        # Garante extensao conhecida para roteamento do parser.
        if target.suffix.lower() != suffix and suffix:
            fixed = target.with_suffix(suffix)
            target.rename(fixed)
            target = fixed
        saved_paths.append(target.resolve())
    return saved_paths


def _cleanup_paths(paths: list[Path]) -> None:
    for file in paths:
        try:
            if file.exists():
                file.unlink()
        except OSError:
            pass


def main() -> None:
    st.set_page_config(page_title="Extrator de Glosas", layout="wide")
    st.title("Extrator de Glosas de Convenios")
    st.write("Faca upload dos demonstrativos (`XML`, `XLSX`, `PDF`) para gerar o resumo e listar somente as glosas.")

    uploaded_files = st.file_uploader(
        "Arquivos do demonstrativo",
        type=["xml", "xlsx", "xls", "pdf"],
        accept_multiple_files=True,
    )
    analyze_clicked = st.button("Analisar arquivos", type="primary", disabled=not uploaded_files)

    if not analyze_clicked:
        return

    if not uploaded_files:
        st.warning("Selecione ao menos um arquivo.")
        return

    saved_paths: list[Path] = []
    try:
        with st.spinner("Processando demonstrativo..."):
            saved_paths = _save_uploaded_files(uploaded_files)
            parsed = parse_inputs(saved_paths)
            dataframe = parsed.dataframe
            glosa_raw = filter_glosa_rows(dataframe)
            glosa_output = output_columns_dataframe(glosa_raw)
            summary = summarize_demonstrativo(dataframe, glosa_raw)

        if parsed.warnings:
            for warning in parsed.warnings:
                st.warning(warning)

        tipo = summary.get("tipo_demonstrativo", "desconhecido")
        if tipo == "pagamento":
            st.info("Tipo detectado: Demonstrativo de Pagamento")
            col1, col2, col3 = st.columns(3)
            col1.metric("Numeracao do protocolo", summary["protocolo_numero"])
            col2.metric("Valor total faturado", _format_currency_brl(summary["valor_total_faturado"]))
            col3.metric("Valor total glosado", _format_currency_brl(summary["valor_total_glosado"]))
        elif tipo == "contas_medicas":
            st.info("Tipo detectado: Demonstrativo de Contas Medicas")
            col1, col2, col3 = st.columns(3)
            col4, col5, col6 = st.columns(3)

            col1.metric("Numeracao do lote", summary["numero_lote"])
            col2.metric("Numeracao do protocolo", summary["protocolo_numero"])
            col3.metric("ANS da operadora", summary["ans_operadora"])
            col4.metric("Valor total faturado", _format_currency_brl(summary["valor_total_faturado"]))
            col5.metric("Valor total glosado", _format_currency_brl(summary["valor_total_glosado"]))
            col6.metric("Quantidade de guias glosadas", str(summary["quantidade_guias_glosadas"]))
        else:
            st.info("Tipo detectado: Demonstrativo nao identificado")
            col1, col2, col3 = st.columns(3)
            col1.metric("Numeracao do protocolo", summary["protocolo_numero"])
            col2.metric("Valor total faturado", _format_currency_brl(summary["valor_total_faturado"]))
            col3.metric("Valor total glosado", _format_currency_brl(summary["valor_total_glosado"]))

        st.subheader("Guias glosadas")
        if glosa_output.empty:
            st.info("Nenhuma glosa identificada nos arquivos enviados.")
            return

        display_df = glosa_output.copy()
        display_df["Valor Glosado"] = pd.to_numeric(display_df["Valor Glosado"], errors="coerce")
        display_df["Valor Glosado"] = display_df["Valor Glosado"].map(
            lambda v: _format_currency_brl(float(v)) if pd.notna(v) else ""
        )

        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.download_button(
            label="Baixar Excel Consolidado",
            data=dataframe_to_excel_bytes(glosa_output),
            file_name="glosas_consolidadas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    finally:
        _cleanup_paths(saved_paths)


if __name__ == "__main__":
    main()
