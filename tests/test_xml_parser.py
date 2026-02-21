from pathlib import Path
from uuid import uuid4

from glosa_extractor.parsers.xml_tiss import parse_xml_tiss


def test_parse_xml_tiss_extracts_basic_glosa_fields():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas">
  <ans:cabecalho>
    <ans:identificacaoOperadora>
      <ans:registroANS>123456</ans:registroANS>
    </ans:identificacaoOperadora>
    <ans:identificacaoPrestador>
      <ans:codigoPrestadorNaOperadora>PREST-01</ans:codigoPrestadorNaOperadora>
    </ans:identificacaoPrestador>
  </ans:cabecalho>
  <ans:prestadorParaOperadora>
    <ans:loteGuias>
      <ans:numeroLote>LOTE-99</ans:numeroLote>
      <ans:guiasTISS>
        <ans:guiaSP-SADT>
          <ans:cabecalhoGuia>
            <ans:numeroGuiaPrestador>GP-001</ans:numeroGuiaPrestador>
            <ans:numeroGuiaOperadora>GO-002</ans:numeroGuiaOperadora>
          </ans:cabecalhoGuia>
          <ans:dadosAutorizacao>
            <ans:senha>SENHA-ABC</ans:senha>
          </ans:dadosAutorizacao>
          <ans:procedimentosExecutados>
            <ans:procedimentoExecutado>
              <ans:dataRealizacao>2026-02-01</ans:dataRealizacao>
              <ans:codigoProcedimento>10101012</ans:codigoProcedimento>
              <ans:descricaoProcedimento>Consulta Clinica</ans:descricaoProcedimento>
              <ans:valorInformado>100,00</ans:valorInformado>
              <ans:valorPago>60,00</ans:valorPago>
              <ans:glosas>
                <ans:glosa>
                  <ans:codigoGlosa>701</ans:codigoGlosa>
                  <ans:valorGlosa>40,00</ans:valorGlosa>
                </ans:glosa>
              </ans:glosas>
            </ans:procedimentoExecutado>
          </ans:procedimentosExecutados>
        </ans:guiaSP-SADT>
      </ans:guiasTISS>
    </ans:loteGuias>
  </ans:prestadorParaOperadora>
</ans:mensagemTISS>
"""
    tmp_dir = Path("tests") / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    xml_file = tmp_dir / f"retorno_{uuid4().hex}.xml"
    try:
        xml_file.write_text(xml_content, encoding="utf-8")
        df = parse_xml_tiss(xml_file)

        assert len(df) == 1
        row = df.iloc[0]
        assert row["ans_operadora"] == "123456"
        assert row["numero_lote"] == "LOTE-99"
        assert row["guia_prestador"] == "GP-001"
        assert row["numero_guia_operadora"] == "GO-002"
        assert row["senha"] == "SENHA-ABC"
        assert row["codigo_procedimento"] == "10101012"
        assert row["tipo_glosa"] == "701"
        assert row["valor_glosado"] == 40.0
    finally:
        if xml_file.exists():
            xml_file.unlink()


def test_parse_xml_tiss_extracts_tipo_glosa_tag():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas">
  <ans:cabecalho>
    <ans:identificacaoOperadora>
      <ans:registroANS>123456</ans:registroANS>
    </ans:identificacaoOperadora>
  </ans:cabecalho>
  <ans:prestadorParaOperadora>
    <ans:loteGuias>
      <ans:numeroLote>10</ans:numeroLote>
      <ans:guiasTISS>
        <ans:guiaSP-SADT>
          <ans:procedimentosExecutados>
            <ans:procedimentoExecutado>
              <ans:codigoProcedimento>99999999</ans:codigoProcedimento>
              <ans:glosas>
                <ans:glosa>
                  <ans:tipoGlosa>710</ans:tipoGlosa>
                  <ans:valorGlosa>15,00</ans:valorGlosa>
                </ans:glosa>
              </ans:glosas>
            </ans:procedimentoExecutado>
          </ans:procedimentosExecutados>
        </ans:guiaSP-SADT>
      </ans:guiasTISS>
    </ans:loteGuias>
  </ans:prestadorParaOperadora>
</ans:mensagemTISS>
"""
    tmp_dir = Path("tests") / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    xml_file = tmp_dir / f"retorno_tipo_glosa_{uuid4().hex}.xml"
    try:
        xml_file.write_text(xml_content, encoding="utf-8")
        df = parse_xml_tiss(xml_file)
        assert len(df) == 1
        row = df.iloc[0]
        assert row["tipo_glosa"] == "710"
        assert row["valor_glosado"] == 15.0
    finally:
        if xml_file.exists():
            xml_file.unlink()


def test_parse_xml_tiss_pagamento_without_procedures_returns_totals():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas">
  <ans:demonstrativoRetorno>
    <ans:demonstrativosRetorno>
      <ans:demonstrativoPagamento>
        <ans:numeroProtocolo>PROTO-999</ans:numeroProtocolo>
        <ans:valorInformadoProtocolo>2000,00</ans:valorInformadoProtocolo>
        <ans:valorLiberadoProtocolo>1700,00</ans:valorLiberadoProtocolo>
        <ans:valorGlosaProtocolo>300,00</ans:valorGlosaProtocolo>
      </ans:demonstrativoPagamento>
    </ans:demonstrativosRetorno>
  </ans:demonstrativoRetorno>
</ans:mensagemTISS>
"""
    tmp_dir = Path("tests") / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    xml_file = tmp_dir / f"retorno_pagamento_{uuid4().hex}.xml"
    try:
        xml_file.write_text(xml_content, encoding="utf-8")
        df = parse_xml_tiss(xml_file)

        assert len(df) == 1
        row = df.iloc[0]
        assert row["tipo_demonstrativo"] == "pagamento"
        assert row["protocolo_numero"] == "PROTO-999"
        assert row["valor_informado_total"] == 2000.0
        assert row["valor_pago_total"] == 1700.0
        assert row["valor_glosado_total"] == 300.0
        assert row["valor_informado"] == 2000.0
        assert row["valor_glosado"] == 300.0
    finally:
        if xml_file.exists():
            xml_file.unlink()


def test_parse_xml_tiss_keeps_protocol_from_each_context():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas">
  <ans:prestadorParaOperadora>
    <ans:relacaoProtocolos>
      <ans:numeroProtocolo>PROTO-A</ans:numeroProtocolo>
      <ans:relacaoGuias>
        <ans:codigoProcedimento>11111111</ans:codigoProcedimento>
        <ans:valorInformado>100,00</ans:valorInformado>
        <ans:valorGlosa>10,00</ans:valorGlosa>
      </ans:relacaoGuias>
    </ans:relacaoProtocolos>
    <ans:relacaoProtocolos>
      <ans:numeroProtocolo>PROTO-B</ans:numeroProtocolo>
      <ans:relacaoGuias>
        <ans:codigoProcedimento>22222222</ans:codigoProcedimento>
        <ans:valorInformado>200,00</ans:valorInformado>
        <ans:valorGlosa>20,00</ans:valorGlosa>
      </ans:relacaoGuias>
    </ans:relacaoProtocolos>
  </ans:prestadorParaOperadora>
</ans:mensagemTISS>
"""
    tmp_dir = Path("tests") / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    xml_file = tmp_dir / f"retorno_multi_proto_{uuid4().hex}.xml"
    try:
        xml_file.write_text(xml_content, encoding="utf-8")
        df = parse_xml_tiss(xml_file)
        protocolos = sorted({str(v).strip() for v in df["protocolo_numero"].tolist() if str(v).strip()})
        assert protocolos == ["PROTO-A", "PROTO-B"]
    finally:
        if xml_file.exists():
            xml_file.unlink()
