import csv
import logging
from typing import List, Dict, Any, TypedDict
from datetime import datetime, date

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Sale(TypedDict):
    produto: str
    valor: float
    data: date

def read_sales_csv(file_path: str) -> List[Sale]:
    sales: List[Sale] = []
    logging.info(f"Iniciando leitura do arquivo CSV: {file_path}")
    try:
        with open(file_path, mode='r', encoding='utf-8', newline='') as file:
            csv_reader = csv.DictReader(file)
            
            expected_headers = ['produto', 'valor', 'data']
            if csv_reader.fieldnames is None:
                error_msg = "CSV vazio ou sem cabeçalho."
                logging.error(error_msg)
                raise ValueError(error_msg)
                
            if not all(header in csv_reader.fieldnames for header in expected_headers):
                 missing = set(expected_headers) - set(csv_reader.fieldnames)
                 error_msg = f"Cabeçalhos ausentes no CSV: {', '.join(missing)}. Esperado: {', '.join(expected_headers)}"
                 logging.error(error_msg)
                 raise ValueError(error_msg)

            for i, line in enumerate(csv_reader):
                line_number = i + 2 
                try:
                    produto = line['produto'].strip()
                    if not produto:
                        raise ValueError("Coluna 'produto' não pode estar vazia.")

                    valor_str = line['valor'].strip().replace(',', '.') 
                    valor = float(valor_str)
                    if valor < 0:
                         raise ValueError("Coluna 'valor' não pode ser negativa.")

                    date_str = line['data'].strip()
                    if not date_str:
                        raise ValueError("Coluna 'data' não pode estar vazia.")
                    sale_date = datetime.strptime(date_str, '%Y-%m-%d').date()

                    sale: Sale = {
                        'produto': produto,
                        'valor': valor,
                        'data': sale_date
                    }
                    sales.append(sale)
                except KeyError as e:
                    logging.warning(f"Linha {line_number}: Coluna essencial ausente '{e}'. Pulando linha.")
                except ValueError as e:
                    logging.warning(f"Linha {line_number}: Erro de valor ou formato - {e}. Linha: {line}. Pulando linha.")
                except Exception as e:
                     logging.warning(f"Linha {line_number}: Erro inesperado ao processar linha {line}: {e}. Pulando linha.")

    except FileNotFoundError:
        logging.error(f"Erro: Arquivo não encontrado em '{file_path}'")
        raise 
    except ValueError as e:
        raise
    except Exception as e:
        logging.error(f"Erro inesperado ao ler o arquivo CSV '{file_path}': {e}")
        raise 

    if not sales:
        logging.warning(f"Nenhuma venda válida encontrada no arquivo {file_path}.")
    else:
        logging.info(f"Leitura do arquivo {file_path} concluída. {len(sales)} sales lidas com sucesso.")
    
    return sales

