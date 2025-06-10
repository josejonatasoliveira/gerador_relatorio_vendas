# CLI de Processamento de Vendas (`vendas-cli`)

Esta é uma ferramenta de linha de comando (CLI) desenvolvida em Python para processar arquivos CSV contendo dados de vendas e gerar relatórios resumidos.

## Funcionalidades

*   **Leitura de CSV:** Lê arquivos CSV com colunas `produto`, `valor` e `data` (formato `AAAA-MM-DD`).
*   **Cálculos:** Calcula o total de vendas por produto, o valor total de todas as vendas e identifica o produto mais vendido (em valor).
*   **Filtros:** Permite filtrar as vendas por um intervalo de datas (opcional).
*   **Formatos de Saída:** Gera relatórios em formato de texto formatado (tabela) ou JSON.
*   **Qualidade:** Código com tipagem estática, estrutura modular, logs e tratamento de erros.
*   **Testes:** Cobertura de testes unitários usando `pytest`.

## Instalação

1.  **Clone o repositório (ou tenha os arquivos do projeto):**
    ```bash
    # git clone https://github.com/josejonatasoliveira/gerador_relatorio_vendas.git
    # cd gerador_relatorio_vendas
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # .venv\Scripts\activate
    ```

3.  **Instale a CLI:**
    Navegue até o diretório raiz do projeto (`gerador_relatorio_vendas`) onde o `pyproject.toml` está localizado e execute:
    ```bash
    pip install .
    ```
    Para instalar também as dependências de desenvolvimento (como `pytest`):
    ```bash
    pip install .[dev]
    ```

## Uso

O comando principal é `vendas-cli`.

**Sintaxe básica:**

```bash
vendas-cli <caminho_para_o_arquivo.csv> [opções]
```

**Argumentos:**

*   `<caminho_para_o_arquivo.csv>`: (Obrigatório) O caminho para o arquivo CSV a ser processado.

**Opções:**

*   `--format {text|json}`: Formato da saída. Padrão: `text`.
*   `--start AAAA-MM-DD`: Data de início para filtrar as vendas (inclusive).
*   `--end AAAA-MM-DD`: Data de fim para filtrar as vendas (inclusive).
*   `-v`, `--verbose`: Ativa logs mais detalhados (nível DEBUG).
*   `-h`, `--help`: Mostra a mensagem de ajuda.

**Exemplos:**

1.  **Gerar relatório em formato texto (padrão) para todas as vendas:**
    ```bash
    vendas-cli dados/vendas.csv
    ```

2.  **Gerar relatório em formato JSON para todas as vendas:**
    ```bash
    vendas-cli dados/vendas.csv --format json
    ```

3.  **Gerar relatório em texto para vendas entre 2025-01-01 e 2025-03-31:**
    ```bash
    vendas-cli dados/vendas.csv --start 2025-01-01 --end 2025-03-31
    ```

4.  **Gerar relatório JSON apenas para vendas a partir de 2025-02-15:**
    ```bash
    vendas-cli dados/vendas.csv --format json --start 2025-02-15
    ```

## Executando os Testes

Certifique-se de ter instalado as dependências de desenvolvimento (`pip install .[dev]`).

No diretório raiz do projeto (`gerador_relatorio_vendas`), execute:

```bash
pytest
```

Para ver o relatório de cobertura de testes:

```bash
pytest --cov=vendas_cli
```

Para gerar um relatório HTML de cobertura (será criado na pasta `htmlcov`):

```bash
pytest --cov=vendas_cli --cov-report=html
```

## Formato Esperado do CSV

O arquivo CSV deve ter as seguintes colunas:

*   `produto`: Nome do produto (texto).
*   `valor`: Valor da venda (número, pode usar `.` ou `,` como separador decimal).
*   `data`: Data da venda no formato `AAAA-MM-DD`.

**Exemplo de `vendas.csv`:**

```csv
produto,valor,data
Produto A,100.50,2025-01-15
Produto B,75,20,2025-01-16
Produto A,50,2025-01-17
Produto C,"200,00",2025-02-10
```