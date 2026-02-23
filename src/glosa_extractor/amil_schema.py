from __future__ import annotations

AMIL_CANONICAL_COLUMNS = [
    "protocolo_numero",
    "numero_lote",
    "beneficiario_nome",
    "beneficiario_codigo",
    "guia_prestador_numero",
    "guia_operadora_numero",
    "data_realizacao",
    "glosa_codigo",
    "glosa_descricao",
    "valor_glosa",
]

AMIL_INTERNAL_COLUMNS = [
    "arquivo_origem",
]

AMIL_ALL_COLUMNS = AMIL_CANONICAL_COLUMNS + AMIL_INTERNAL_COLUMNS

AMIL_EXPORT_COLUMNS = [
    "protocolo_numero",
    "numero_lote",
    "beneficiario_nome",
    "beneficiario_codigo",
    "guia_prestador_numero",
    "guia_operadora_numero",
    "data_realizacao",
    "glosa_codigo",
    "glosa_descricao",
    "valor_glosa",
]

AMIL_EXPORT_HEADERS = {
    "protocolo_numero": "Número do Protocolo",
    "numero_lote": "Número do Lote",
    "beneficiario_nome": "Nome do Beneficiário",
    "beneficiario_codigo": "Código do Beneficiário",
    "guia_prestador_numero": "Número da Guia no Prestador",
    "guia_operadora_numero": "Número da Guia Atribuído pela Operadora",
    "data_realizacao": "Data Realização",
    "glosa_codigo": "Código da Glosa da Guia",
    "glosa_descricao": "Descrição Glosa",
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
    "beneficiario_nome": {
        "nome do beneficiario",
        "nome beneficiario",
        "beneficiario",
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
    "data_realizacao": {
        "data realizacao",
        "data de realizacao",
        "data atendimento",
        "data procedimento",
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
    "valor_glosa": {
        "valor glosa",
        "valor da glosa",
        "valor glosa r",
        "valor glosado",
    },
}
