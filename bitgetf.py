import requests
import json
import os
from datetime import datetime

def fetch_bitget_futures_tickers(product_type="umcbl"):
    """
    Faz uma requisição à API de Futuros (Mix) da Bitget para obter todos os tickers
    e seus preços atuais. Por padrão, usa 'umcbl' (USDT margined).
    Retorna um dicionário no formato: { "BTCUSDT_UMCBL": float(preco), ... }
    """
    url = f"https://api.bitget.com/api/mix/v1/market/tickers?productType={product_type}"
    response = requests.get(url)
    data = response.json()

    # Verifica se o retorno da API é bem-sucedido
    if data.get("code") != "00000":
        raise Exception(f"Erro ao buscar dados da Bitget Futuros: {data.get('msg')}")

    tickers_dict = {}
    # "last" é o último preço negociado
    for item in data["data"]:
        symbol = item["symbol"]     # Exemplo: "BTCUSDT_UMCBL"
        try:
            last_price = float(item["last"])
        except ValueError:
            continue
        tickers_dict[symbol] = last_price
    
    return tickers_dict

def get_latest_futures_file():
    """
    Retorna o nome do arquivo mais recente que comece com 'bitget_futures_'
    e termine em '.json'. Caso não exista nenhum, retorna None.
    """
    files = [f for f in os.listdir('.') if f.startswith("bitget_futures_") and f.endswith(".json")]
    if not files:
        return None
    # Ordena pelo timestamp no nome, do mais antigo para o mais recente
    files_sorted = sorted(files, key=lambda x: x.replace("bitget_futures_", "").replace(".json", ""))
    return files_sorted[-1]  # o último é o mais recente

def load_json_file(filepath):
    """
    Lê um arquivo JSON e retorna o dicionário correspondente.
    Se o arquivo não existir ou ocorrer erro, retorna {}.
    """
    if not filepath or not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao ler {filepath}: {e}")
        return {}

def save_json_file(data, filepath):
    """
    Salva o dicionário 'data' em um arquivo JSON com indentação.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Arquivo '{filepath}' criado com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar arquivo {filepath}: {e}")

def remove_oldest_if_exceeds(limit=2):
    """
    Se existirem mais que 'limit' arquivos que comecem com 'bitget_futures_',
    apaga o mais antigo (com base no timestamp no nome).
    """
    files = [f for f in os.listdir('.') if f.startswith("bitget_futures_") and f.endswith(".json")]
    if len(files) > limit:
        files_sorted = sorted(files, key=lambda x: x.replace("bitget_futures_", "").replace(".json", ""))
        oldest = files_sorted[0]
        os.remove(oldest)
        print(f"Excluído o arquivo mais antigo: {oldest}")

def main():
    # 1. Carrega o arquivo bitget_futures mais recente (para comparar)
    latest_file = get_latest_futures_file()
    old_data = load_json_file(latest_file) if latest_file else {}

    # 2. Busca dados atuais de Futuros USDT (UMCBL) na Bitget
    new_data = fetch_bitget_futures_tickers(product_type="umcbl")

    # 3. Identifica símbolos novos (presentes agora, mas ausentes no arquivo anterior)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_tickers_list = []
    for symbol, price in new_data.items():
        if symbol not in old_data:
            new_tickers_list.append({
                "symbol": symbol,
                "price": price,
                "detected_at": now_str
            })

    # 4. Cria arquivo 'novo_bitget_futures.json' com os tickers detectados
    diff_output = {
        "script_run_at": now_str,
        "new_tickers": new_tickers_list
    }
    save_json_file(diff_output, "novo_bitget_futures.json")

    # 5. Salva os dados atuais em 'bitget_futures_YYYY-MM-DD_HH-MM-SS.json'
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    futures_filename = f"bitget_futures_{timestamp}.json"
    save_json_file(new_data, futures_filename)

    # 6. Mantém no máximo 2 arquivos bitget_futures_*.json
    remove_oldest_if_exceeds(limit=2)

if __name__ == "__main__":
    main()
