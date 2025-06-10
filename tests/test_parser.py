import pytest
import os
from datetime import date
from vendas_cli.parser import read_sales_csv, Sale

@pytest.fixture
def csv_valid(tmp_path):
    content = "produto,valor,data\nProduto A,100.50,2025-01-15\nProduto B,75.2,2025-01-16\nProduto A,50,2025-01-17"
    file_path = tmp_path / "valido.csv"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)

@pytest.fixture
def csv_with_errors(tmp_path):
    content = (
        "produto,valor,data\n"
        "Produto A,100.50,2025-01-15\n"
        "Produto B,invalido,2025-01-16\n"
        "Produto C,50,2025/01/17\n"
        "Produto D,-10,2025-01-18\n"
        ",20,2025-01-19\n"
        "Produto F,30,\n"
        "Produto G,10,2025-01-20\n"
    )
    file_path = tmp_path / "erros.csv"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)

@pytest.fixture
def csv_invalid_header(tmp_path):
    content = "item,preco,quando\nProduto A,100.50,2025-01-15"
    file_path = tmp_path / "cabecalho_invalido.csv"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)

@pytest.fixture
def empty_csv(tmp_path):
    content = "produto,valor,data"
    file_path = tmp_path / "vazio.csv"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)

@pytest.fixture
def csv_without_header(tmp_path):
    content = "Produto A,100.50,2025-01-15\nProduto B,200,2025-01-16"
    file_path = tmp_path / "sem_cabecalho.csv"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)

def test_read_valid_csv(csv_valid):
    # GIVEN
    sales = read_sales_csv(csv_valid)

    # WHEN/THEN
    assert len(sales) == 3
    assert sales[0] == Sale(produto="Produto A", valor=100.50, data=date(2025, 1, 15))
    assert sales[1] == Sale(produto="Produto B", valor=75.20, data=date(2025, 1, 16))
    assert sales[2] == Sale(produto="Produto A", valor=50.00, data=date(2025, 1, 17))

def test_read_sales_csv_ignore_invalid_lines(csv_with_errors, caplog):
    # GIVEN
    sales = read_sales_csv(csv_with_errors)

    # WHEN/THEN
    assert len(sales) == 2 
    assert sales[0]["produto"] == "Produto A"
    assert sales[1]["produto"] == "Produto G"
    assert "Linha 3: Erro de valor ou formato" in caplog.text
    assert "Linha 4: Erro de valor ou formato" in caplog.text
    assert "Linha 5: Erro de valor ou formato" in caplog.text
    assert "Linha 6: Erro de valor ou formato" in caplog.text
    assert "Linha 7: Erro de valor ou formato" in caplog.text

def test_read_sales_csv_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_sales_csv("arquivo_inexistente.csv")

def test_read_empty_csv(empty_csv, caplog):
    # GIVEN
    sales = read_sales_csv(empty_csv)

    # WHEN/THEN
    assert len(sales) == 0
    assert "Nenhuma venda válida encontrada" in caplog.text

def test_read_sales_csv_with_invalid_header(csv_invalid_header):
    with pytest.raises(ValueError, match=r"Cabeçalhos ausentes no CSV: .* Esperado: produto, valor, data"):
        read_sales_csv(csv_invalid_header)

@pytest.fixture
def csv_empty(tmp_path):
    # GIVEN
    file_path = tmp_path / "realmente_vazio.csv"

    # WHEN
    file_path.touch()

    # THEN
    return str(file_path)

def test_read_sales_csv_from_empty_csv(csv_empty):
     with pytest.raises(ValueError, match="CSV vazio ou sem cabeçalho."):
         read_sales_csv(csv_empty)

def test_read_sales_csv_with_header_and_without_data(csv_without_header):
    with pytest.raises(ValueError, match=r"Cabeçalhos ausentes no CSV: .* Esperado: produto, valor, data"):
        read_sales_csv(csv_without_header)

@pytest.fixture
def csv_with_comma_decimal(tmp_path):
    # GIVEN
    content = 'produto,valor,data\nProduto A,"100,50",2025-01-15\nProduto B,"75,2",2025-01-16'
    file_path = tmp_path / "virgula.csv"

    # WHEN
    file_path.write_text(content, encoding="utf-8")

    # THEN
    return str(file_path)

def test_read_sales_csv_with_comma_decimal(csv_with_comma_decimal):
    # GIVEN
    sales = read_sales_csv(csv_with_comma_decimal)

    # WHEN/THEN
    assert len(sales) == 2
    assert sales[0]["valor"] == 100.50
    assert sales[1]["valor"] == 75.20

