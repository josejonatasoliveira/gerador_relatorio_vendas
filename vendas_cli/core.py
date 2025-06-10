from typing import List, Dict, Tuple, Optional, TypedDict
from collections import defaultdict
import logging
from datetime import date

class Sale(TypedDict):
    produto: str
    valor: float
    data: date

class SaleMetrics(TypedDict):
    total_por_produto: Dict[str, float]
    valor_total_vendas: float
    produto_mais_vendido: Optional[Tuple[str, float]]


def calculate_sales_metrics(sales: List[Sale]) -> SaleMetrics:
    logging.info(f"Iniciando cálculo de métricas para {len(sales)} s.")
    if not sales:
        logging.warning("Lista de vendas vazia. Retornando métricas zeradas.")
        return {
            'total_por_produto': {},
            'valor_total_vendas': 0.0,
            'produto_mais_vendido': None
        }

    total_per_product: Dict[str, float] = defaultdict(float)
    sales_total_value: float = 0.0

    for sale in sales:
        try:
            product = sale['produto']
            value = sale['valor']
            
            total_per_product[product] += value
            sales_total_value += value
        except KeyError as e:
            logging.warning(f"Registro de venda inválido encontrado durante o cálculo: {sale}. Chave ausente: {e}. Ignorando registro.")
        except TypeError as e:
             logging.warning(f"Registro de venda com tipo inválido encontrado: {sale}. Erro: {e}. Ignorando registro.")

    best_selling_product: Optional[Tuple[str, float]] = None
    if total_per_product:
        best_selling_product = max(total_per_product.items(), key=lambda item: item[1])
        logging.info(f"Produto mais vendido: {best_selling_product[0]} com total de R$ {best_selling_product[1]:.2f}")
    else:
        logging.info("Nenhum produto encontrado para determinar o mais vendido.")

    logging.info(f"Cálculo de métricas concluído. Valor total: R$ {sales_total_value:.2f}")

    metrics: SaleMetrics = {
        'total_por_produto': dict(total_per_product),
        'valor_total_vendas': sales_total_value,
        'produto_mais_vendido': best_selling_product
    }
    
    return metrics

if __name__ == '__main__':
    example_sales: List[Sale] = [
        {'produto': 'Produto A', 'valor': 100.50, 'data': date(2025, 1, 15)},
        {'produto': 'Produto B', 'valor': 75.20, 'data': date(2025, 1, 16)},
        {'produto': 'Produto A', 'valor': 50.00, 'data': date(2025, 1, 17)},
        {'produto': 'Produto C', 'valor': 200.00, 'data': date(2025, 1, 18)},
        {'produto': 'Produto B', 'valor': 25.80, 'data': date(2025, 1, 19)},
    ]

    metrics = calculate_sales_metrics(example_sales)
    print("Métricas Calculadas:")
    print(f" - Total por Produto: {metrics['total_por_produto']}")
    print(f" - Valor Total Geral: {metrics['valor_total_vendas']:.2f}")
    if metrics['produto_mais_vendido']:
        print(f" - Produto Mais Vendido: {metrics['produto_mais_vendido'][0]} (R$ {metrics['produto_mais_vendido'][1]:.2f})")
    else:
        print(" - Produto Mais Vendido: Nenhum")

