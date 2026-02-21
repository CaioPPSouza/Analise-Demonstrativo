# Extrator de Glosas de Convenios

Utilitario de linha de comando para ler demonstrativos em `XML`, `XLSX` e `PDF`, consolidar dados e gerar um `Excel` apenas com itens glosados.

## Instalacao

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev,ui]
```

## Uso

```powershell
extrator-glosas --input .\entrada --output .\glosas_consolidadas.xlsx
```

Tambem aceita multiplos caminhos:

```powershell
extrator-glosas --input .\retorno1.xml .\demonstrativo.xlsx --output .\saida.xlsx
```

## Tela Web (Interface)

```powershell
extrator-glosas-ui
```

A tela permite:
- upload de um ou mais arquivos (`XML`, `XLSX`, `PDF`)
- deteccao automatica do tipo de demonstrativo (`contas medicas` ou `pagamento`)
- resumo do demonstrativo:
  - numeracao do lote
  - numeracao do protocolo
  - ANS da operadora
  - valor total faturado
  - valor total glosado
  - quantidade de guias glosadas
- visualizacao das glosas e download do Excel consolidado

## Colunas de Saida

- `Número Lote`
- `PrestadorNúmero`
- `ProtocoloNúmero`
- `Guia Prestador`
- `Senha`
- `Número Guia Operadora`
- `Data Realização`
- `Código Procedimento`
- `Descrição Procedimento`
- `Tipo Glosa`
- `Valor Glosado`
