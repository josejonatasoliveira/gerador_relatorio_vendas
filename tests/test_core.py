import pytest
from datetime import date
from vendas_cli.core import calculate_sales_metrics, Sale
from typing import List, Optional, Tuple, Any

EXAMPLE_SALES: List[Sale] = [

    Sale(produto="Produto A", valor=100.50, data=date(2025, 1, 15)),
    Sale(produto="Produto B", valor=75.20, data=date(2025, 1, 16)),
    Sale(produto="Produto A", valor=50.00, data=date(2025, 1, 17)),
    Sale(produto="Produto C", valor=200.00, data=date(2025, 2, 10)),
    Sale(produto="Produto B", valor=25.80, data=date(2025, 2, 15)),
]

EMPTY_SALES: List[Sale] = []

ONE_SALE: List[Sale] = [
    Sale(produto="Produto Unico", valor=500.00, data=date(2025, 3, 1))
]

def test_calculate_sales_metrics_with_empty_list(caplog):
    # GIVEN
    metrics = calculate_sales_metrics(EMPTY_SALES)

    # WHEN/THEN
    assert metrics["valor_total_vendas"] == 0.0
    assert metrics["total_por_produto"] == {}
    assert metrics["produto_mais_vendido"] is None
    assert "Lista de vendas vazia" in caplog.text

def test_calculate_sales_metrics_with_sales():
    # GIVEN
    metrics = calculate_sales_metrics(EXAMPLE_SALES)
    
    # WHEN/THEN
    assert metrics["valor_total_vendas"] == pytest.approx(100.50 + 75.20 + 50.00 + 200.00 + 25.80)
    
    assert len(metrics["total_por_produto"]) == 3
    assert metrics["total_por_produto"]["Produto A"] == pytest.approx(100.50 + 50.00)
    assert metrics["total_por_produto"]["Produto B"] == pytest.approx(75.20 + 25.80)
    assert metrics["total_por_produto"]["Produto C"] == pytest.approx(200.00)
    
    assert metrics["produto_mais_vendido"] is not None
    product_ms, value_ms = metrics["produto_mais_vendido"]
    assert product_ms == "Produto C"
    assert value_ms == pytest.approx(200.00)

def test_calculate_sales_metrics_with_one_sale():
    # GIVEN
    metrics = calculate_sales_metrics(ONE_SALE)

    # WHEN/THEN
    assert metrics["valor_total_vendas"] == 500.00
    assert metrics["total_por_produto"] == {"Produto Unico": 500.00}
    assert metrics["produto_mais_vendido"] == ("Produto Unico", 500.00)

def test_calculate_sales_metrics_with_invalid_data(caplog):
    # GIVEN
    invalid_sales = [
        Sale(produto="Valido", valor=10.0, data=date(2025, 1, 1)),
        {"prod": "Invalido", "valor": 20.0, "data": date(2025, 1, 2)},
        {"produto": "Outro Valido", "valor": None, "data": date(2025, 1, 3)}
    ]
    invalid_sales_any: List[Any] = invalid_sales 
    
    # WHEN
    metrics = calculate_sales_metrics(invalid_sales_any)
    
    # THEN
    assert metrics["valor_total_vendas"] == 10.0
    assert "Valido" in metrics["total_por_produto"]
    assert metrics["total_por_produto"]["Valido"] == 10.0
    if "Outro Valido" in metrics["total_por_produto"]:
        assert metrics["total_por_produto"]["Outro Valido"] == 0.0
        
    assert metrics["produto_mais_vendido"] == ("Valido", 10.0)
    
    assert "Chave ausente: 'produto'" in caplog.text
    assert "Registro de venda com tipo inválido" in caplog.text

