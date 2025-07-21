import pytest
import json
from datetime import date
from vendas_cli.parser import Sale
from vendas_cli.core import SaleMetrics
from vendas_cli.output import (
    filter_sales_by_date,
    format_text,
    format_json,
    generate_report
)
from typing import List, Optional

FILTER_SALES: List[Sale] = [
    Sale(produto="P1", valor=10.0, data=date(2025, 1, 10)),
    Sale(produto="P2", valor=20.0, data=date(2025, 1, 15)), 
    Sale(produto="P3", valor=30.0, data=date(2025, 1, 20)),
    Sale(produto="P4", valor=40.0, data=date(2025, 1, 5)),
    Sale(produto="P5", valor=50.0, data=date(2025, 1, 25)),
]

EXAMPLE_METRICS: SaleMetrics = {
    "total_por_produto": {"Produto A": 150.5, "Produto B": 101.0, "Produto C": 200.0},
    "valor_total_vendas": 451.5,
    "produto_mais_vendido": ("Produto C", 200.0)
}

EMPTY_METRICS: SaleMetrics = {
    "total_por_produto": {},
    "valor_total_vendas": 0.0,
    "produto_mais_vendido": None
}

@pytest.mark.parametrize(
    "start_date, end_date, expected_indexes",
    [
        (date(2025, 1, 15), date(2025, 1, 20), [1, 2]),
        (date(2025, 1, 15), None, [1, 2, 4]),
        (None, date(2025, 1, 15), [0, 1, 3]),          
        (None, None, [0, 1, 2, 3, 4]),        
        (date(2025, 2, 1), date(2025, 2, 10), []),  
        (date(2025, 1, 10), date(2025, 1, 10), [0]),   
    ]
)
def test_filtrar_vendas_por_data(start_date: Optional[date], end_date: Optional[date], expected_indexes: List[int]):
    # GIVEN
    result = filter_sales_by_date(FILTER_SALES, start_date, end_date)

    # WHEN/THEN
    assert len(result) == len(expected_indexes)
    expected_products = [FILTER_SALES[i]["produto"] for i in expected_indexes]
    result_products = [v["produto"] for v in result]
    assert sorted(result_products) == sorted(expected_products)

def test_filtrar_vendas_lista_vazia():
    # GIVEN
    result = filter_sales_by_date([], date(2025, 1, 1), date(2025, 1, 31))

    # WHEN/THEN
    assert result == []

def test_formatar_texto_com_dados():
    # GIVEN
    text = format_text(EXAMPLE_METRICS)

    # WHEN/THEN
    assert "--- Relatório de Vendas ---" in text
    assert "Vendas Totais por Produto:" in text
    assert "Produto A" in text
    assert "150.50" in text
    assert "Produto B" in text
    assert "101.00" in text
    assert "Produto C" in text
    assert "200.00" in text
    assert "Valor Total Geral das Vendas: R$ 451.50" in text
    assert "Produto Mais Vendido: Produto C (R$ 200.00)" in text
    assert "+" in text and "-" in text and "|" in text

def test_formatar_texto_sem_dados():
    # GIVEN
    text = format_text(EMPTY_METRICS)

    # WHEN/THEN
    assert "--- Relatório de Vendas ---" in text
    assert "Nenhuma venda encontrada." in text
    assert "Valor Total Geral das Vendas: R$ 0.00" in text
    assert "Produto Mais Vendido: N/A (Nenhuma venda)" in text

def test_formatar_json_com_dados():
    # GIVEN
    json_str = format_json(EXAMPLE_METRICS)

    # WHEN/THEN
    try:
        result = json.loads(json_str)
    except json.JSONDecodeError:
        pytest.fail("Saída JSON inválida")

    assert result["total_por_produto"]["Produto A"] == 150.5
    assert result["total_por_produto"]["Produto B"] == 101.0
    assert result["total_por_produto"]["Produto C"] == 200.0
    assert result["valor_total_vendas"] == 451.5
    assert result["produto_mais_vendido"]["produto"] == "Produto C"
    assert result["produto_mais_vendido"]["valor_total"] == 200.0

def test_formatar_json_sem_dados():
    # GIVEN
    json_str = format_json(EMPTY_METRICS)

    # WHEN/THEN
    try:
        result = json.loads(json_str)
    except json.JSONDecodeError:
        pytest.fail("Saída JSON inválida")

    assert result["total_por_produto"] == {}
    assert result["valor_total_vendas"] == 0.0
    assert result["produto_mais_vendido"] is None

def test_gerar_relatorio_texto():
    # GIVEN
    report = generate_report(EXAMPLE_METRICS, "text")

    # WHEN/THEN
    assert "--- Relatório de Vendas ---" in report

def test_gerar_relatorio_json():
    # GIVEN
    report = generate_report(EXAMPLE_METRICS, "json")

    # WHEN/THEN
    try:
        json.loads(report)
    except json.JSONDecodeError:
        pytest.fail("generate_report não produziu JSON válido para formato=	json	")

def test_gerar_relatorio_formato_invalido():
    # GIVEN/WHEN/THEN
    with pytest.raises(ValueError, match=r"Formato de saída inválido:\s*invalido\s*. Use 'text' ou 'json'."):
        generate_report(EXAMPLE_METRICS, "invalido")

