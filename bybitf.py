import requests
import json
import os
from datetime import datetime

def fetch_bybit_futures_linears():
    """
    Faz uma requisição à API de Futuros (Bybit v5) para obter todos os tickers
    de Perpetual Linear (margined em USDT).
    Retorna um dicionário no formato: { "BTCUSDT": 30000.0, ... }
    """
    url = "https://api.bybit.com/v5/market/tickers?category=linear"
    response = requests.get(url)
    
    # Caso precise de debug:
    # print(f"Status code: {response.status_code}")
    # print(f"Snippet da resposta: {response.text[:200]}")

    data = response.json()

    if data.get("retCode") != 0:
        raise Exception(f"Erro da Bybit v5 (Linear Futuros): {data.get('retMsg')}")

    tickers_dict = {}
    results_list = data.get("result", {}).get("list", [])

    for item in results_list:
        symbol = item["symbol"]            # Ex.: "BTCUSDT"
        last_price_str = item["lastPrice"] # Ex.: "30000"
        try:
            last_price = float(last_price_str)
            tickers_dict[symbol] = last_price
        except ValueError:
            continue

    return tickers_dict

def get_latest_bybit_futures_file():
    """
    Retorna o arquivo mais recente que comece com 'bybit_futures_'
    e termine em '.json'. Se não existir, retorna None.
    """
    files = [f for f in os.listdir('.') if f.startswith("bybit_futures_") and f.endswith(".json")]
    if not files:
        return None
    # Ordenar do mais antigo para o mais recente
    files_sorted = sorted(files, key=lambda x: x.replace("bybit_futures_", "").replace(".json", ""))
    return files_sorted[-1]  # o último é o mais recente

def load_json_file(filepath):
    """
    Lê um arquivo JSON e retorna o dicionário correspondente.
    Se não existir ou ocorrer erro, retorna {}.
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
    Se existirem mais de 'limit' arquivos que comecem com 'bybit_futures_',
    remove o mais antigo (com base no timestamp no nome).
    """
    files = [f for f in os.listdir('.') if f.startswith("bybit_futures_") and f.endswith(".json")]
    if len(files) > limit:
        files_sorted = sorted(files, key=lambda x: x.replace("bybit_futures_", "").replace(".json", ""))
        oldest = files_sorted[0]
        os.remove(oldest)
        print(f"Excluído o arquivo mais antigo: {oldest}")

def main():
    # 1. Carrega o arquivo bybit_futures mais recente (para comparar)
    latest_file = get_latest_bybit_futures_file()
    old_data = load_json_file(latest_file) if latest_file else {}

    # 2. Busca dados atuais de Futuros Linear (USDT) da Bybit
    new_data = fetch_bybit_futures_linears()

    # 3. Identifica símbolos novos (presentes agora, mas não no arquivo anterior)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_tickers_list = []
    for symbol, price in new_data.items():
        if symbol not in old_data:
            new_tickers_list.append({
                "symbol": symbol,
                "price": price,
                "detected_at": now_str
            })

    # 4. Cria o arquivo 'novo_bybit_futures.json' com os símbolos novos
    diff_output = {
        "script_run_at": now_str,
        "new_tickers": new_tickers_list
    }
    save_json_file(diff_output, "novo_bybit_futures.json")

    # 5. Salva todos os dados atuais em 'bybit_futures_YYYY-MM-DD_HH-MM-SS.json'
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    futures_filename = f"bybit_futures_{timestamp}.json"
    save_json_file(new_data, futures_filename)

    # 6. Mantém no máximo 2 arquivos 'bybit_futures_*.json'
    remove_oldest_if_exceeds(limit=2)

if __name__ == "__main__":
    main()
