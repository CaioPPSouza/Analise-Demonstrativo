from pathlib import Path
from uuid import uuid4

import pandas as pd

from glosa_extractor.pipeline import process_inputs


def test_pipeline_uses_amil_schema_when_selected():
    input_df = pd.DataFrame(
        {
            "Número do Protocolo": ["PROTO-1"],
            "Número do Lote": ["LOTE-1"],
            "Código do Beneficiário": ["BEN-1"],
            "Número da Guia no Prestador": ["GP-1"],
            "Número da Guia Atribuído pela Operadora": ["GO-1"],
            "Senha": ["TR2025010000001"],
            "Data Realização": ["2026-02-10"],
            "Código Procedimento": ["50000470"],
            "Descrição Procedimento": ["Sessão de Psicoterapia"],
            "Código da Glosa da Guia": ["9001"],
            "Descrição Glosa": ["Sem cobertura"],
            "Definições da glosa": ["Regra X"],
            "Valor Glosa (R$)": ["88,70"],
        }
    )

    tmp_dir = Path("tests") / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    xlsx_file = tmp_dir / f"pipeline_amil_{uuid4().hex}.xlsx"
    try:
        input_df.to_excel(xlsx_file, index=False)

        result = process_inputs([xlsx_file], convenio="amil")

        assert result.convenio == "amil"
        assert "Número do Protocolo" in result.dataframe.columns
        assert "Valor Glosa (R$)" in result.dataframe.columns
        assert "Código Procedimento" in result.dataframe.columns
        assert "Descrição Procedimento" in result.dataframe.columns
        assert len(result.dataframe) == 1
    finally:
        if xlsx_file.exists():
            xlsx_file.unlink()


def test_pipeline_defaults_to_bradesco():
    input_df = pd.DataFrame(
        {
            "Número Lote": ["L-1"],
            "ProtocoloNúmero": ["P-1"],
            "Guia Prestador": ["GP-1"],
            "Tipo Glosa": ["701"],
            "Valor Glosado": [42.0],
        }
    )

    tmp_dir = Path("tests") / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    xlsx_file = tmp_dir / f"pipeline_bradesco_{uuid4().hex}.xlsx"
    try:
        input_df.to_excel(xlsx_file, index=False)

        result = process_inputs([xlsx_file])

        assert result.convenio == "bradesco"
        assert "Código Procedimento" in result.dataframe.columns
        assert "Valor Glosado" in result.dataframe.columns
    finally:
        if xlsx_file.exists():
            xlsx_file.unlink()
