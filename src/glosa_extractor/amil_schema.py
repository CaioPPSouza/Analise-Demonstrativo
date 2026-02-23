from __future__ import annotations

AMIL_CANONICAL_COLUMNS = [
    "protocolo_numero",
    "numero_lote",
    "beneficiario_codigo",
    "guia_prestador_numero",
    "guia_operadora_numero",
    "senha",
    "data_realizacao",
    "codigo_procedimento",
    "descricao_procedimento",
    "glosa_codigo",
    "glosa_descricao",
    "glosa_definicao",
    "valor_glosa",
]

AMIL_INTERNAL_COLUMNS = [
    "arquivo_origem",
]

AMIL_ALL_COLUMNS = AMIL_CANONICAL_COLUMNS + AMIL_INTERNAL_COLUMNS

AMIL_EXPORT_COLUMNS = [
    "protocolo_numero",
    "numero_lote",
    "beneficiario_codigo",
    "guia_prestador_numero",
    "guia_operadora_numero",
    "senha",
    "data_realizacao",
    "codigo_procedimento",
    "descricao_procedimento",
    "glosa_codigo",
    "glosa_descricao",
    "glosa_definicao",
    "valor_glosa",
]

AMIL_EXPORT_HEADERS = {
    "protocolo_numero": "Número do Protocolo",
    "numero_lote": "Número do Lote",
    "beneficiario_codigo": "Código do Beneficiário",
    "guia_prestador_numero": "Número da Guia no Prestador",
    "guia_operadora_numero": "Número da Guia Atribuído pela Operadora",
    "senha": "Senha",
    "data_realizacao": "Data Realização",
    "codigo_procedimento": "Código Procedimento",
    "descricao_procedimento": "Descrição Procedimento",
    "glosa_codigo": "Código da Glosa da Guia",
    "glosa_descricao": "Descrição Glosa",
    "glosa_definicao": "Definições da glosa",
    "valor_glosa": "Valor Glosa (R$)",
}

AMIL_HEADER_ALIASES = {
    "protocolo_numero": {
        "numero do protocolo",
        "numero protocolo",
        "n do protocolo",
        "n protocolo",
        "protocolo",
    },
    "numero_lote": {
        "numero do lote",
        "numero lote",
        "n do lote",
        "n lote",
        "lote",
    },
    "beneficiario_codigo": {
        "codigo do beneficiario",
        "codigo beneficiario",
        "cod beneficiario",
        "carteirinha",
        "numero carteirinha",
    },
    "guia_prestador_numero": {
        "numero da guia no prestador",
        "numero guia no prestador",
        "numero guia prestador",
        "guia no prestador",
        "guia prestador",
    },
    "guia_operadora_numero": {
        "numero da guia atribuido pela operadora",
        "numero guia atribuido pela operadora",
        "numero guia operadora",
        "guia operadora",
        "guia atribuida pela operadora",
    },
    "senha": {
        "senha",
        "numero senha",
        "senha autorizacao",
        "senha autorização",
    },
    "data_realizacao": {
        "data realizacao",
        "data de realizacao",
        "data atendimento",
        "data procedimento",
    },
    "codigo_procedimento": {
        "codigo procedimento",
        "procedimento codigo",
        "cod procedimento",
        "codigo_procedimento",
    },
    "descricao_procedimento": {
        "descricao procedimento",
        "procedimento",
        "nome procedimento",
        "descricao_procedimento",
    },
    "glosa_codigo": {
        "codigo da glosa da guia",
        "codigo glosa da guia",
        "codigo glosa",
        "cod glosa",
        "glosa codigo",
    },
    "glosa_descricao": {
        "descricao glosa",
        "descricao da glosa",
        "motivo glosa",
    },
    "glosa_definicao": {
        "definicoes da glosa",
        "definicao da glosa",
        "definicoes glosa",
        "definicao glosa",
    },
    "valor_glosa": {
        "valor glosa",
        "valor da glosa",
        "valor glosa r",
        "valor glosado",
    },
}
