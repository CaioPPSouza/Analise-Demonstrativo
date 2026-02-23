from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from glosa_extractor.convenios import DEFAULT_CONVENIO, list_convenios
from glosa_extractor.excel_writer import dataframe_to_excel_bytes
from glosa_extractor.pipeline import process_inputs


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
    st.write("Selecione o convenio e faca upload dos demonstrativos (`XML`, `XLSX`, `PDF`) para listar somente as glosas.")

    convenio_configs = list_convenios()
    convenio_labels = [config.label for config in convenio_configs]
    convenio_by_label = {config.label: config for config in convenio_configs}

    default_label = next(
        (config.label for config in convenio_configs if config.key == DEFAULT_CONVENIO),
        convenio_labels[0],
    )
    convenio_label = st.selectbox("Convênio", options=convenio_labels, index=convenio_labels.index(default_label))
    convenio_config = convenio_by_label[convenio_label]
    allowed_file_types = ["xml", "xlsx", "xls", "pdf"]

    uploaded_files = st.file_uploader(
        "Arquivos do demonstrativo",
        type=allowed_file_types,
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
            result = process_inputs(saved_paths, convenio=convenio_config.key)

        if result.warnings:
            for warning in result.warnings:
                st.warning(warning)

        summary = result.summary
        if convenio_config.key == "amil":
            st.info("Convênio selecionado: AMIL")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Número do lote", summary["numero_lote"])
            col2.metric("Número do protocolo", summary["protocolo_numero"])
            col3.metric("Valor total glosado", _format_currency_brl(summary["valor_total_glosado"]))
            col4.metric("Quantidade de guias glosadas", str(summary["quantidade_guias_glosadas"]))
        else:
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
        glosa_output = result.dataframe
        if glosa_output.empty:
            st.info("Nenhuma glosa identificada nos arquivos enviados.")
            return

        display_df = glosa_output.copy()

        for currency_col in ("Valor Glosado", "Valor Glosa (R$)"):
            if currency_col in display_df.columns:
                display_df[currency_col] = pd.to_numeric(display_df[currency_col], errors="coerce")
                display_df[currency_col] = display_df[currency_col].map(
                    lambda v: _format_currency_brl(float(v)) if pd.notna(v) else ""
                )

        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.download_button(
            label="Baixar Excel Consolidado",
            data=dataframe_to_excel_bytes(glosa_output),
            file_name=f"glosas_consolidadas_{convenio_config.key}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    finally:
        _cleanup_paths(saved_paths)


if __name__ == "__main__":
    main()
