from pathlib import Path
from uuid import uuid4

from glosa_extractor.amil_reporting import filter_glosa_rows
from glosa_extractor.parsers.amil_xml_tiss import parse_xml_tiss_amil


def test_parse_xml_tiss_amil_extracts_guia_level_glosa():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas">
  <ans:operadoraParaPrestador>
    <ans:demonstrativosRetorno>
      <ans:demonstrativoAnaliseConta>
        <ans:dadosConta>
          <ans:dadosProtocolo>
            <ans:numeroLotePrestador>7728177</ans:numeroLotePrestador>
            <ans:numeroProtocolo>5480053391</ans:numeroProtocolo>
            <ans:relacaoGuias>
              <ans:numeroGuiaPrestador>296369878</ans:numeroGuiaPrestador>
              <ans:numeroGuiaOperadora>296369878</ans:numeroGuiaOperadora>
              <ans:senha>TR2025011257630</ans:senha>
              <ans:numeroCarteira>081190656</ans:numeroCarteira>
              <ans:motivoGlosaGuia>
                <ans:codigoGlosa>3052</ans:codigoGlosa>
                <ans:descricaoGlosa>DOCUMENTACAO INCOMPLETA</ans:descricaoGlosa>
              </ans:motivoGlosaGuia>
              <ans:detalhesGuia>
                <ans:dataRealizacao>2025-10-24</ans:dataRealizacao>
                <ans:procedimento>
                  <ans:codigoProcedimento>50000470</ans:codigoProcedimento>
                  <ans:descricaoProcedimento>Sessao de Psicoterapia</ans:descricaoProcedimento>
                </ans:procedimento>
              </ans:detalhesGuia>
              <ans:valorGlosaGuia>28.88</ans:valorGlosaGuia>
            </ans:relacaoGuias>
            <ans:relacaoGuias>
              <ans:numeroGuiaPrestador>296010016</ans:numeroGuiaPrestador>
              <ans:numeroGuiaOperadora>296010016</ans:numeroGuiaOperadora>
              <ans:senha>TR2025011099634</ans:senha>
              <ans:numeroCarteira>845676440</ans:numeroCarteira>
              <ans:detalhesGuia>
                <ans:dataRealizacao>2025-10-21</ans:dataRealizacao>
                <ans:procedimento>
                  <ans:codigoProcedimento>50000470</ans:codigoProcedimento>
                  <ans:descricaoProcedimento>Sessao de Psicoterapia</ans:descricaoProcedimento>
                </ans:procedimento>
              </ans:detalhesGuia>
            </ans:relacaoGuias>
          </ans:dadosProtocolo>
        </ans:dadosConta>
      </ans:demonstrativoAnaliseConta>
    </ans:demonstrativosRetorno>
  </ans:operadoraParaPrestador>
</ans:mensagemTISS>
"""
    tmp_dir = Path("tests") / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    xml_file = tmp_dir / f"amil_guia_glosa_{uuid4().hex}.xml"
    try:
        xml_file.write_text(xml_content, encoding="utf-8")
        df = parse_xml_tiss_amil(xml_file)
        glosa_df = filter_glosa_rows(df)

        assert len(df) == 2
        assert len(glosa_df) == 1
        row = glosa_df.iloc[0]
        assert row["protocolo_numero"] == "5480053391"
        assert row["numero_lote"] == "7728177"
        assert row["beneficiario_codigo"] == "081190656"
        assert row["guia_prestador_numero"] == "296369878"
        assert row["guia_operadora_numero"] == "296369878"
        assert row["senha"] == "TR2025011257630"
        assert row["codigo_procedimento"] == "50000470"
        assert row["descricao_procedimento"] == "Sessao de Psicoterapia"
        assert row["glosa_codigo"] == "3052"
        assert row["glosa_descricao"] == "DOCUMENTACAO INCOMPLETA"
        assert row["glosa_definicao"] == ""
        assert row["valor_glosa"] == 28.88
        assert row["data_realizacao"] == "24-10-2025"
    finally:
        if xml_file.exists():
            xml_file.unlink()


def test_parse_xml_tiss_amil_extracts_item_relacao_glosa():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<ans:mensagemTISS xmlns:ans="http://www.ans.gov.br/padroes/tiss/schemas">
  <ans:operadoraParaPrestador>
    <ans:demonstrativosRetorno>
      <ans:demonstrativoAnaliseConta>
        <ans:dadosConta>
          <ans:dadosProtocolo>
            <ans:numeroLotePrestador>1000</ans:numeroLotePrestador>
            <ans:numeroProtocolo>PROTO-XYZ</ans:numeroProtocolo>
            <ans:relacaoGuias>
              <ans:numeroGuiaPrestador>GP-1</ans:numeroGuiaPrestador>
              <ans:numeroGuiaOperadora>GO-1</ans:numeroGuiaOperadora>
              <ans:senha>SENHA-XYZ</ans:senha>
              <ans:numeroCarteira>CART-1</ans:numeroCarteira>
              <ans:detalhesGuia>
                <ans:dataRealizacao>2025-10-21</ans:dataRealizacao>
                <ans:procedimento>
                  <ans:codigoProcedimento>50000560</ans:codigoProcedimento>
                  <ans:descricaoProcedimento>Consulta Ambulatorial</ans:descricaoProcedimento>
                </ans:procedimento>
                <ans:valorInformado>28.88</ans:valorInformado>
                <ans:valorLiberado>0</ans:valorLiberado>
                <ans:relacaoGlosa>
                  <ans:tipoGlosa>1702</ans:tipoGlosa>
                  <ans:valorGlosa>28.88</ans:valorGlosa>
                </ans:relacaoGlosa>
              </ans:detalhesGuia>
            </ans:relacaoGuias>
          </ans:dadosProtocolo>
        </ans:dadosConta>
      </ans:demonstrativoAnaliseConta>
    </ans:demonstrativosRetorno>
  </ans:operadoraParaPrestador>
</ans:mensagemTISS>
"""
    tmp_dir = Path("tests") / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    xml_file = tmp_dir / f"amil_item_glosa_{uuid4().hex}.xml"
    try:
        xml_file.write_text(xml_content, encoding="utf-8")
        df = parse_xml_tiss_amil(xml_file)
        glosa_df = filter_glosa_rows(df)

        assert len(df) == 1
        assert len(glosa_df) == 1
        row = glosa_df.iloc[0]
        assert row["protocolo_numero"] == "PROTO-XYZ"
        assert row["numero_lote"] == "1000"
        assert row["beneficiario_codigo"] == "CART-1"
        assert row["senha"] == "SENHA-XYZ"
        assert row["codigo_procedimento"] == "50000560"
        assert row["descricao_procedimento"] == "Consulta Ambulatorial"
        assert row["glosa_codigo"] == "1702"
        assert row["glosa_definicao"] == ""
        assert row["valor_glosa"] == 28.88
    finally:
        if xml_file.exists():
            xml_file.unlink()
