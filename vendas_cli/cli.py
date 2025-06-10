import argparse
import logging
import sys
from datetime import datetime, date
from typing import Optional, Sequence

from vendas_cli.parser import read_sales_csv, Sale
from vendas_cli.core import calculate_sales_metrics
from vendas_cli.output import filter_sales_by_date, generate_report

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logger = logging.getLogger(__name__)

def validate_date(date_str: str) -> date:
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"Formato de data inválido: 	{date_str}	. Use AAAA-MM-DD.")

def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Processa um arquivo CSV de vendas e gera relatórios.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "arquivo_csv",
        help="Caminho para o arquivo CSV de vendas."
    )

    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Formato de saída do relatório (padrão: text)."
    )
    parser.add_argument(
        "--start",
        type=validate_date,
        help="Data de início para filtrar vendas (formato AAAA-MM-DD)."
    )
    parser.add_argument(
        "--end",
        type=validate_date,
        help="Data de fim para filtrar vendas (formato AAAA-MM-DD)."
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Aumenta o nível de log para DEBUG."
    )

    args = parser.parse_args(argv)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Logging configurado para DEBUG.")

    logger.info(f"Iniciando processamento do arquivo: {args.arquivo_csv}")
    logger.debug(f"Argumentos recebidos: {args}")

    try:
        gross_sales = read_sales_csv(args.arquivo_csv)

        sales_filtered = filter_sales_by_date(gross_sales, args.start, args.end)

        if not sales_filtered:
            logger.warning("Nenhuma venda encontrada para o período especificado (ou o arquivo estava vazio/inválido).")
            print("Nenhuma venda encontrada para processar com os filtros aplicados.", file=sys.stderr)
            return 1 

        metrics = calculate_sales_metrics(sales_filtered)

        report = generate_report(metrics, args.format)

        print(report)
        logger.info("Relatório gerado com sucesso.")
        return 0

    except FileNotFoundError:
        logger.error(f"Erro: O arquivo CSV 	{args.arquivo_csv}	 não foi encontrado.")
        print(f"Erro: Arquivo não encontrado: {args.arquivo_csv}", file=sys.stderr)
        return 1
    except ValueError as e:
        logger.error(f"Erro de valor ou formato nos dados: {e}")
        print(f"Erro nos dados do arquivo ou argumentos: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.exception(f"Ocorreu um erro inesperado durante o processamento: {e}") # Usar exception para incluir traceback no log
        print(f"Erro inesperado: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())

