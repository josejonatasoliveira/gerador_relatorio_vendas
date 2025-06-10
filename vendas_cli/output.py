import json
import logging
from typing import List, Dict, Optional, Any
from datetime import date
from tabulate import tabulate

from vendas_cli.parser import Sale
from vendas_cli.core import SaleMetrics


def filter_sales_by_date(sales: List[Sale], start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Sale]:
   
    if start_date is None and end_date is None:
        logging.debug("Nenhum filtro de data aplicado.")
        return sales

    sales_filtered: List[Sale] = []
    log_msg_parts = ["Filtrando vendas"]
    if start_date:
        log_msg_parts.append(f"a partir de {start_date.isoformat()}")
    if end_date:
        log_msg_parts.append(f"até {end_date.isoformat()}")
    logging.info(" ".join(log_msg_parts) + ".")

    for sale in sales:
        try:
            sale_date = sale["data"]
            start_match = start_date is None or sale_date >= start_date
            end_match = end_date is None or sale_date <= end_date
            
            if start_match and end_match:
                sales_filtered.append(sale)
        except KeyError:
            logging.warning(f"Registro de venda inválido encontrado durante a filtragem: {sale}. Ignorando.")
        except TypeError:
             logging.warning(f"Registro de venda com data inválida encontrado durante a filtragem: {sale}. Ignorando.")

    logging.info(f"{len(sales_filtered)} vendas encontradas no período especificado.")
    return sales_filtered

def format_text(metrics: SaleMetrics) -> str:
    output_lines = []
    output_lines.append("--- Relatório de Vendas ---")

    output_lines.append("\nVendas Totais por Produto:")
    if metrics["total_por_produto"]:
        product_tables = [
            [produto, f"R$ {valor:.2f}"] 
            for produto, valor in sorted(metrics["total_por_produto"].items())
        ]
        output_lines.append(tabulate(product_tables, headers=["Produto", "Valor Total"], tablefmt="grid"))
    else:
        output_lines.append("Nenhuma venda encontrada.")

    output_lines.append(f"\nValor Total Geral das Vendas: R$ {metrics['valor_total_vendas']:.2f}")

    most_sold = metrics["produto_mais_vendido"]
    if most_sold:
        output_lines.append(f"Produto Mais Vendido: {most_sold[0]} (R$ {most_sold[1]:.2f})")
    else:
        output_lines.append("Produto Mais Vendido: N/A (Nenhuma venda)")
        
    output_lines.append("\n---------------------------")
    return "\n".join(output_lines)

def format_json(metrics: SaleMetrics) -> str:
    
    serializable_metrics = {
        "total_por_produto": metrics["total_por_produto"],
        "valor_total_vendas": metrics["valor_total_vendas"],
        "produto_mais_vendido": {
            "produto": metrics["produto_mais_vendido"][0],
            "valor_total": metrics["produto_mais_vendido"][1]
        } if metrics["produto_mais_vendido"] else None
    }
    try:
        return json.dumps(serializable_metrics, indent=4, ensure_ascii=False)
    except TypeError as e:
        logging.error(f"Erro ao serializar métricas para JSON: {e}")
        return json.dumps({"erro": "Falha ao gerar JSON", "detalhes": str(e)}, indent=4)

def generate_report(metrics: SaleMetrics, format: str) -> str:
   
    logging.info(f"Gerando relatório no formato: {format}")
    if format == "text":
        return format_text(metrics)
    elif format == "json":
        return format_json(metrics)
    else:
        error_msg = f"Formato de saída inválido: 	{format}	. Use 'text' ou 'json'."
        logging.error(error_msg)
        raise ValueError(error_msg)

