from pathlib import Path
from uuid import uuid4

import pandas as pd

from glosa_extractor.amil_glosa_catalog import apply_glosa_catalog_fallback


def test_apply_glosa_catalog_fallback_fills_description_and_definition(monkeypatch):
    tmp_dir = Path("tests") / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    catalog_dir = tmp_dir / f"glosa_catalog_{uuid4().hex}"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    catalog_file = catalog_dir / "Códigos de Glosas.txt"
    catalog_file.write_text(
        "\n".join(
            [
                "1603 = Descrição Glosa: TIPO DE CONSULTA INVÁLIDO, Definições = Procedimento com Função Indevida",
                "2812 = = Descrição Glosa: PACOTE NÃO AUTORIZADO. = PACOTE FATURADO NÃO AUTORIZADO",
                "2603 = Descrição Glosa: COBRANÇA DE HONORÁRIO SEM REGISTRO DA EFETIVA PARTICIPAÇÃO DO PROFISSIONAL - Definições da glosa: Conselho Executante Inválido",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("AMIL_GLOSA_CODES_DIR", str(catalog_dir.resolve()))

    df = pd.DataFrame(
        [
            {
                "protocolo_numero": "P1",
                "numero_lote": "L1",
                "beneficiario_codigo": "C1",
                "guia_prestador_numero": "G1",
                "guia_operadora_numero": "G1",
                "senha": "S1",
                "data_realizacao": "01-01-2026",
                "codigo_procedimento": "50000470",
                "descricao_procedimento": "Sessao de Psicoterapia",
                "glosa_codigo": "1603",
                "glosa_descricao": "",
                "glosa_definicao": "",
                "valor_glosa": 10.0,
                "arquivo_origem": "x.xml",
            },
            {
                "protocolo_numero": "P2",
                "numero_lote": "L2",
                "beneficiario_codigo": "C2",
                "guia_prestador_numero": "G2",
                "guia_operadora_numero": "G2",
                "senha": "S2",
                "data_realizacao": "01-01-2026",
                "codigo_procedimento": "50000470",
                "descricao_procedimento": "Sessao de Psicoterapia",
                "glosa_codigo": "2812",
                "glosa_descricao": "",
                "glosa_definicao": "",
                "valor_glosa": 20.0,
                "arquivo_origem": "y.xml",
            },
            {
                "protocolo_numero": "P3",
                "numero_lote": "L3",
                "beneficiario_codigo": "C3",
                "guia_prestador_numero": "G3",
                "guia_operadora_numero": "G3",
                "senha": "S3",
                "data_realizacao": "01-01-2026",
                "codigo_procedimento": "50000470",
                "descricao_procedimento": "Sessao de Psicoterapia",
                "glosa_codigo": "2603",
                "glosa_descricao": "",
                "glosa_definicao": "",
                "valor_glosa": 30.0,
                "arquivo_origem": "z.xml",
            },
        ]
    )

    out = apply_glosa_catalog_fallback(df)

    assert out.iloc[0]["glosa_descricao"] == "TIPO DE CONSULTA INVÁLIDO"
    assert out.iloc[0]["glosa_definicao"] == "Procedimento com Função Indevida"
    assert out.iloc[1]["glosa_descricao"] == "PACOTE NÃO AUTORIZADO."
    assert out.iloc[1]["glosa_definicao"] == "PACOTE FATURADO NÃO AUTORIZADO"
    assert (
        out.iloc[2]["glosa_descricao"]
        == "COBRANÇA DE HONORÁRIO SEM REGISTRO DA EFETIVA PARTICIPAÇÃO DO PROFISSIONAL"
    )
    assert out.iloc[2]["glosa_definicao"] == "Conselho Executante Inválido"
