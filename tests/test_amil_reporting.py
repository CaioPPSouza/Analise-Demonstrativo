from pathlib import Path
from uuid import uuid4

import pandas as pd

from glosa_extractor.amil_reporting import (
    filter_glosa_rows,
    output_columns_dataframe,
    parse_inputs,
    summarize_demonstrativo,
)


def test_parse_amil_xlsx_extracts_only_glosa_rows():
    input_df = pd.DataFrame(
        {
            "Número do Protocolo": ["PROTO-1", "PROTO-1"],
            "Número do Lote": ["LOTE-9", "LOTE-9"],
            "Código do Beneficiário": ["BEN-001", "BEN-002"],
            "Número da Guia no Prestador": ["GP-001", "GP-002"],
            "Número da Guia Atribuído pela Operadora": ["GO-001", "GO-002"],
            "Senha": ["SENHA-001", "SENHA-002"],
            "Data Realização": ["2026-02-15", "2026-02-16"],
            "Código Procedimento": ["50000470", "50000560"],
            "Descrição Procedimento": ["Sessão", "Consulta"],
            "Código da Glosa da Guia": ["", "7501"],
            "Descrição Glosa": ["", "Procedimento não autorizado"],
            "Definições da glosa": ["", "Regra contratual"],
            "Valor Glosa (R$)": ["0,00", "120,50"],
        }
    )

    tmp_dir = Path("tests") / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    xlsx_file = tmp_dir / f"amil_{uuid4().hex}.xlsx"
    try:
        input_df.to_excel(xlsx_file, index=False)

        parsed = parse_inputs([xlsx_file])
        glosa_df = filter_glosa_rows(parsed.dataframe)
        output_df = output_columns_dataframe(glosa_df)
        summary = summarize_demonstrativo(parsed.dataframe, glosa_df)

        assert len(glosa_df) == 1
        assert len(output_df) == 1
        assert output_df.iloc[0]["Código da Glosa da Guia"] == "7501"
        assert output_df.iloc[0]["Valor Glosa (R$)"] == 120.5
        assert summary["numero_lote"] == "LOTE-9"
        assert summary["protocolo_numero"] == "PROTO-1"
        assert summary["valor_total_glosado"] == 120.5
        assert summary["quantidade_guias_glosadas"] == 1
    finally:
        if xlsx_file.exists():
            xlsx_file.unlink()


def test_amil_output_columns_match_required_business_headers():
    row = {
        "protocolo_numero": "PROTO-2",
        "numero_lote": "LOTE-5",
        "beneficiario_codigo": "BEN-123",
        "guia_prestador_numero": "GP-123",
        "guia_operadora_numero": "GO-123",
        "senha": "SENHA-123",
        "data_realizacao": "20-02-2026",
        "codigo_procedimento": "50000470",
        "descricao_procedimento": "Sessão de Psicoterapia",
        "glosa_codigo": "403",
        "glosa_descricao": "Descrição",
        "glosa_definicao": "Definição",
        "valor_glosa": 55.0,
        "arquivo_origem": "amil_teste.xlsx",
    }
    glosa_df = pd.DataFrame([row])
    output_df = output_columns_dataframe(glosa_df)

    assert list(output_df.columns) == [
        "Número do Protocolo",
        "Número do Lote",
        "Código do Beneficiário",
        "Número da Guia no Prestador",
        "Número da Guia Atribuído pela Operadora",
        "Senha",
        "Data Realização",
        "Código Procedimento",
        "Descrição Procedimento",
        "Código da Glosa da Guia",
        "Descrição Glosa",
        "Definições da glosa",
        "Valor Glosa (R$)",
    ]
