from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .convenios import DEFAULT_CONVENIO, list_convenios
from .excel_writer import write_dataframe_to_excel
from .pipeline import process_inputs


def build_parser() -> argparse.ArgumentParser:
    convenio_options = [config.key for config in list_convenios()]
    parser = argparse.ArgumentParser(
        prog="extrator-glosas",
        description="Extrai e consolida guias glosadas de XML, XLSX e PDF.",
    )
    parser.add_argument(
        "--input",
        nargs="+",
        required=True,
        help="Arquivos e/ou pastas de entrada.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Caminho do arquivo .xlsx de saida.",
    )
    parser.add_argument(
        "--convenio",
        choices=convenio_options,
        default=DEFAULT_CONVENIO,
        help="Convenio para aplicar regras de leitura e exportacao.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    input_paths = [Path(item).expanduser().resolve() for item in args.input]
    output_path = Path(args.output).expanduser().resolve()

    result = process_inputs(input_paths, convenio=args.convenio)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_dataframe_to_excel(result.dataframe, output_path)

    for warning in result.warnings:
        print(f"[aviso] {warning}", file=sys.stderr)

    print(f"Arquivo gerado: {output_path}")
    print(f"Convenio processado: {result.convenio}")
    print(f"Itens glosados encontrados: {len(result.dataframe)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
