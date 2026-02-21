import pandas as pd

from glosa_extractor.reporting import (
    detect_demonstrativo_tipo,
    filter_glosa_rows,
    output_columns_dataframe,
    summarize_demonstrativo,
)
from glosa_extractor.schema import ALL_COLUMNS


def test_filter_glosa_rows_and_summary_metrics():
    rows = [
        {
            "ans_operadora": "123456",
            "numero_lote": "LOTE-1",
            "prestador_numero": "P-1",
            "protocolo_numero": "PROTO-9",
            "guia_prestador": "GP-1",
            "senha": "S1",
            "numero_guia_operadora": "GO-1",
            "data_realizacao": "2026-02-01",
            "codigo_procedimento": "101",
            "descricao_procedimento": "Consulta",
            "tipo_glosa": "",
            "valor_glosado": None,
            "valor_informado": 100.0,
            "valor_pago": 100.0,
            "arquivo_origem": "a.xml",
        },
        {
            "ans_operadora": "123456",
            "numero_lote": "LOTE-1",
            "prestador_numero": "P-1",
            "protocolo_numero": "PROTO-9",
            "guia_prestador": "GP-2",
            "senha": "S2",
            "numero_guia_operadora": "GO-2",
            "data_realizacao": "2026-02-01",
            "codigo_procedimento": "202",
            "descricao_procedimento": "Exame",
            "tipo_glosa": "701",
            "valor_glosado": 40.0,
            "valor_informado": 200.0,
            "valor_pago": 160.0,
            "arquivo_origem": "a.xml",
        },
    ]
    df = pd.DataFrame(rows).reindex(columns=ALL_COLUMNS)

    glosa_df = filter_glosa_rows(df)
    summary = summarize_demonstrativo(df, glosa_df)

    assert len(glosa_df) == 1
    assert summary["numero_lote"] == "LOTE-1"
    assert summary["protocolo_numero"] == "PROTO-9"
    assert summary["ans_operadora"] == "123456"
    assert summary["valor_total_faturado"] == 300.0
    assert summary["valor_total_glosado"] == 40.0
    assert summary["quantidade_guias_glosadas"] == 1


def test_output_columns_dataframe_uses_required_headers():
    rows = [
        {
            "ans_operadora": "123456",
            "numero_lote": "50",
            "prestador_numero": "0001",
            "protocolo_numero": "ABC",
            "guia_prestador": "GP-1",
            "senha": "SENHA",
            "numero_guia_operadora": "GO-1",
            "data_realizacao": "24-09-2025",
            "codigo_procedimento": "84250925",
            "descricao_procedimento": "Teste",
            "tipo_glosa": "3062",
            "valor_glosado": 103.5,
            "valor_informado": 103.5,
            "valor_pago": 0.0,
            "arquivo_origem": "arquivo.xml",
        }
    ]
    df = pd.DataFrame(rows).reindex(columns=ALL_COLUMNS)
    out = output_columns_dataframe(df)

    assert list(out.columns) == [
        "Número Lote",
        "PrestadorNúmero",
        "ProtocoloNúmero",
        "Guia Prestador",
        "Senha",
        "Número Guia Operadora",
        "Data Realização",
        "Código Procedimento",
        "Descrição Procedimento",
        "Tipo Glosa",
        "Valor Glosado",
    ]
    assert out.iloc[0]["Valor Glosado"] == 103.5


def test_detect_demonstrativo_tipo_pagamento_por_coluna():
    rows = [
        {
            "ans_operadora": "",
            "numero_lote": "",
            "prestador_numero": "",
            "protocolo_numero": "PROTO-1",
            "guia_prestador": "",
            "senha": "",
            "numero_guia_operadora": "",
            "data_realizacao": "",
            "codigo_procedimento": "",
            "descricao_procedimento": "",
            "tipo_glosa": "",
            "valor_glosado": None,
            "valor_informado": None,
            "valor_pago": None,
            "valor_informado_total": 1000.0,
            "valor_pago_total": 900.0,
            "valor_glosado_total": 100.0,
            "tipo_demonstrativo": "pagamento",
            "arquivo_origem": "pag.xml",
        }
    ]
    df = pd.DataFrame(rows).reindex(columns=ALL_COLUMNS)
    assert detect_demonstrativo_tipo(df) == "pagamento"


def test_summary_uses_total_columns_without_double_counting():
    rows = []
    for idx in range(2):
        rows.append(
            {
                "ans_operadora": "005711",
                "numero_lote": "50",
                "prestador_numero": "0001",
                "protocolo_numero": "PROTO-1",
                "guia_prestador": f"GP-{idx}",
                "senha": "",
                "numero_guia_operadora": "",
                "data_realizacao": "",
                "codigo_procedimento": "",
                "descricao_procedimento": "",
                "tipo_glosa": "",
                "valor_glosado": 50.0,
                "valor_informado": 100.0,
                "valor_pago": 50.0,
                "valor_informado_total": 1000.0,
                "valor_pago_total": 900.0,
                "valor_glosado_total": 100.0,
                "tipo_demonstrativo": "pagamento",
                "arquivo_origem": "pag.xml",
            }
        )
    df = pd.DataFrame(rows).reindex(columns=ALL_COLUMNS)
    glosa_df = filter_glosa_rows(df)
    summary = summarize_demonstrativo(df, glosa_df)

    assert summary["tipo_demonstrativo"] == "pagamento"
    assert summary["valor_total_faturado"] == 1000.0
    assert summary["valor_total_glosado"] == 100.0


def test_summary_contas_medicas_uses_protocol_totals_when_available():
    rows = [
        {
            "ans_operadora": "005711",
            "numero_lote": "50",
            "prestador_numero": "0001",
            "protocolo_numero": "PROTO-ABC",
            "guia_prestador": "GP-1",
            "senha": "",
            "numero_guia_operadora": "",
            "data_realizacao": "24-09-2025",
            "codigo_procedimento": "111",
            "descricao_procedimento": "Proc 1",
            "tipo_glosa": "3062",
            "valor_glosado": 103.5,
            "valor_informado": 103.5,
            "valor_pago": 0.0,
            "valor_informado_total": 11178.0,
            "valor_pago_total": 10660.5,
            "valor_glosado_total": 517.5,
            "tipo_demonstrativo": "contas_medicas",
            "arquivo_origem": "contas.xml",
        },
        {
            "ans_operadora": "005711",
            "numero_lote": "50",
            "prestador_numero": "0001",
            "protocolo_numero": "PROTO-ABC",
            "guia_prestador": "GP-2",
            "senha": "",
            "numero_guia_operadora": "",
            "data_realizacao": "08-10-2025",
            "codigo_procedimento": "222",
            "descricao_procedimento": "Proc 2",
            "tipo_glosa": "3062",
            "valor_glosado": 103.5,
            "valor_informado": 103.5,
            "valor_pago": 0.0,
            "valor_informado_total": 11178.0,
            "valor_pago_total": 10660.5,
            "valor_glosado_total": 517.5,
            "tipo_demonstrativo": "contas_medicas",
            "arquivo_origem": "contas.xml",
        },
    ]
    df = pd.DataFrame(rows).reindex(columns=ALL_COLUMNS)
    glosa_df = filter_glosa_rows(df)
    summary = summarize_demonstrativo(df, glosa_df)

    assert summary["tipo_demonstrativo"] == "contas_medicas"
    assert summary["valor_total_faturado"] == 11178.0
    assert summary["valor_total_glosado"] == 517.5
