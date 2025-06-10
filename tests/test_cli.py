import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock
from datetime import date

from vendas_cli.cli import main

@pytest.fixture
def valid_csv_cli(tmp_path):
    content = "produto,valor,data\nProdA,10.0,2025-01-15\nProdB,20.0,2025-01-20\nProdA,5.0,2025-01-25"
    file_path = tmp_path / "vendas_cli_valido.csv"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)

@pytest.fixture
def empty_csv_cli(tmp_path):
    content = "produto,valor,data"
    file_path = tmp_path / "vendas_cli_vazio.csv"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)

@pytest.fixture
def csv_with_error_cli(tmp_path):
    content = "produto,valor,data\nProdA,10.0,2025-01-15\nProdB,abc,2025-01-20"
    file_path = tmp_path / "vendas_cli_erro.csv"
    file_path.write_text(content, encoding="utf-8")
    return str(file_path)

def test_cli_success_with_json_text(valid_csv_cli, capsys):
    # GIVEN
    argv = [valid_csv_cli]

    # WHEN
    exit_code = main(argv)
    captured = capsys.readouterr()
    
    # THEN
    assert exit_code == 0
    assert "--- Relatório de Vendas ---" in captured.out
    assert "ProdA" in captured.out
    assert "15.00" in captured.out # 10.0 + 5.0
    assert "ProdB" in captured.out
    assert "20.00" in captured.out
    assert "Valor Total Geral das Vendas: R$ 35.00" in captured.out
    assert "Produto Mais Vendido: ProdB (R$ 20.00)" in captured.out
    assert captured.err == ""

def test_cli_success_with_json_format(valid_csv_cli, capsys):
    # GIVEN
    argv = [valid_csv_cli, "--format", "json"]

    # WHEN
    exit_code = main(argv)
    captured = capsys.readouterr()
    
    # THEN
    assert exit_code == 0
    assert captured.err == ""
    try:
        data = json.loads(captured.out)

        assert data["total_por_produto"]["ProdA"] == 15.0
        assert data["total_por_produto"]["ProdB"] == 20.0
        assert data["valor_total_vendas"] == 35.0
        assert data["produto_mais_vendido"]["produto"] == "ProdB"
        assert data["produto_mais_vendido"]["valor_total"] == 20.0
    except json.JSONDecodeError:
        pytest.fail("Saída não é um JSON válido")

def test_cli_success_with_date_filter(valid_csv_cli, capsys):
    # GIVEN
    argv = [valid_csv_cli, "--start", "2025-01-16", "--end", "2025-01-30"]

    # WHEN
    exit_code = main(argv)
    captured = capsys.readouterr()
    
    # THEN
    assert exit_code == 0
    assert "ProdA" in captured.out
    assert "5.00" in captured.out 
    assert "ProdB" in captured.out
    assert "20.00" in captured.out
    assert "Valor Total Geral das Vendas: R$ 25.00" in captured.out
    assert "Produto Mais Vendido: ProdB (R$ 20.00)" in captured.out
    assert captured.err == ""

def test_cli_file_not_found(capsys):
    # GIVEN
    argv = ["arquivo_inexistente.csv"]

    # WHEN
    exit_code = main(argv)
    captured = capsys.readouterr()
    
    # THEN
    assert exit_code == 1
    assert "Erro: Arquivo não encontrado" in captured.err
    assert captured.out == ""

def test_cli_invalid_date_format(valid_csv_cli, capsys):
    # GIVEN
    argv = [valid_csv_cli, "--start", "15-01-2025"]

    # WHEN/THEN
    with pytest.raises(SystemExit) as e:
        main(argv)
    assert e.value.code == 2
    captured = capsys.readouterr() 
    assert "argument --start" in captured.err
    assert "Formato de data inválido: \t15-01-2025\t. Use AAAA-MM-DD." in captured.err

def test_cli_invalid_output_format(valid_csv_cli, capsys):
    # GIVEN
    argv = [valid_csv_cli, "--format", "yaml"]

    # WHEN/THEN
    with pytest.raises(SystemExit) as e:
        main(argv)
    assert e.value.code == 2
    captured = capsys.readouterr()
    assert "argument --format: invalid choice: 'yaml'" in captured.err

def test_cli_empty_csv(empty_csv_cli, capsys):
    # GIVEN
    argv = [empty_csv_cli]

    # WHEN
    exit_code = main(argv)
    captured = capsys.readouterr()
    
    # THEN
    assert exit_code == 1
    assert "Nenhuma venda encontrada para processar" in captured.err
    assert captured.out == ""

def test_cli_csv_with_proccess_error(csv_com_erro_cli, capsys):
    # GIVEN
    argv = [csv_com_erro_cli]

    # WHEN
    exit_code = main(argv)
    captured = capsys.readouterr()
    
    # THEN
    assert exit_code == 0
    assert "--- Relatório de Vendas ---" in captured.out
    assert "ProdA" in captured.out
    assert "10.00" in captured.out
    assert "ProdB" not in captured.out
    assert "Valor Total Geral das Vendas: R$ 10.00" in captured.out
    assert "Produto Mais Vendido: ProdA (R$ 10.00)" in captured.out
    assert captured.err == ""

def test_cli_without_required_argument(capsys):
    # GIVEN
    argv = []

    # WHEN/THEN
    with pytest.raises(SystemExit) as e:
        main(argv)
    assert e.value.code == 2
    captured = capsys.readouterr()
    assert "the following arguments are required: arquivo_csv" in captured.err

def test_cli_verbose_mode(valid_csv_cli, caplog):
    # GIVEN
    import logging

    # WHEN
    logging.getLogger().setLevel(logging.INFO)
    argv = [valid_csv_cli, "-v"]

    # THEN
    with caplog.at_level(logging.DEBUG):
        exit_code = main(argv)
    
    assert exit_code == 0
    assert "Logging configurado para DEBUG." in caplog.text
    assert "Argumentos recebidos:" in caplog.text

