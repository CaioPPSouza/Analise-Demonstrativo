from __future__ import annotations

CANONICAL_COLUMNS = [
    "ans_operadora",
    "numero_lote",
    "prestador_numero",
    "protocolo_numero",
    "guia_prestador",
    "senha",
    "numero_guia_operadora",
    "data_realizacao",
    "codigo_procedimento",
    "descricao_procedimento",
    "tipo_glosa",
    "valor_glosado",
]

INTERNAL_COLUMNS = [
    "valor_informado",
    "valor_pago",
    "valor_informado_total",
    "valor_pago_total",
    "valor_glosado_total",
    "tipo_demonstrativo",
    "arquivo_origem",
]

ALL_COLUMNS = CANONICAL_COLUMNS + INTERNAL_COLUMNS

EXPORT_COLUMNS = [
    "numero_lote",
    "prestador_numero",
    "protocolo_numero",
    "guia_prestador",
    "senha",
    "numero_guia_operadora",
    "data_realizacao",
    "codigo_procedimento",
    "descricao_procedimento",
    "tipo_glosa",
    "valor_glosado",
]

EXPORT_HEADERS = {
    "numero_lote": "Número Lote",
    "prestador_numero": "PrestadorNúmero",
    "protocolo_numero": "ProtocoloNúmero",
    "guia_prestador": "Guia Prestador",
    "senha": "Senha",
    "numero_guia_operadora": "Número Guia Operadora",
    "data_realizacao": "Data Realização",
    "codigo_procedimento": "Código Procedimento",
    "descricao_procedimento": "Descrição Procedimento",
    "tipo_glosa": "Tipo Glosa",
    "valor_glosado": "Valor Glosado",
}

HEADER_ALIASES = {
    "ans_operadora": {
        "ans da operadora",
        "registro ans",
        "registroans",
        "registro ans operadora",
        "ans_operadora",
    },
    "numero_lote": {
        "numero lote",
        "n lote",
        "lote",
        "numerolote",
        "numero_lote",
    },
    "prestador_numero": {
        "prestador",
        "prestador/numero",
        "codigo prestador",
        "codigo prestador na operadora",
        "codigo prestador operadora",
        "prestador_numero",
    },
    "protocolo_numero": {
        "protocolo",
        "protocolo/numero",
        "numero protocolo",
        "numeroprotocolo",
        "protocolo_numero",
    },
    "guia_prestador": {
        "guia prestador",
        "numero guia prestador",
        "numeroguiaprestador",
        "guia_prestador",
    },
    "senha": {
        "senha",
        "senha autorizacao",
        "numero senha",
    },
    "numero_guia_operadora": {
        "numero guia operadora",
        "guia operadora",
        "numeroguiaoperadora",
        "numero_guia_operadora",
    },
    "data_realizacao": {
        "data realizacao",
        "data atendimento",
        "data procedimento",
        "data_realizacao",
    },
    "codigo_procedimento": {
        "codigo procedimento",
        "procedimento codigo",
        "cod procedimento",
        "tuss",
        "codigo_procedimento",
    },
    "descricao_procedimento": {
        "descricao procedimento",
        "procedimento",
        "nome procedimento",
        "descricao_procedimento",
    },
    "tipo_glosa": {
        "tipo glosa",
        "codigo glosa",
        "motivo glosa",
        "glosa",
        "tipo_glosa",
    },
    "valor_glosado": {
        "valor glosado",
        "valor glosa",
        "vl glosa",
        "valor_glosado",
    },
    "valor_informado": {
        "valor informado",
        "vl informado",
        "valor cobrado",
        "valor_informado",
    },
    "valor_pago": {
        "valor pago",
        "vl pago",
        "valor liberado",
        "valor_pago",
    },
    "valor_informado_total": {
        "valor total faturado",
        "valor informado total",
        "valor informado protocolo",
        "valor informado geral",
        "valor_informado_total",
    },
    "valor_pago_total": {
        "valor total pago",
        "valor total liberado",
        "valor pago total",
        "valor liberado total",
        "valor_pago_total",
    },
    "valor_glosado_total": {
        "valor total glosado",
        "valor glosa total",
        "valor glosa protocolo",
        "valor glosa geral",
        "valor_glosado_total",
    },
    "tipo_demonstrativo": {
        "tipo demonstrativo",
        "tipo_demonstrativo",
    },
}
