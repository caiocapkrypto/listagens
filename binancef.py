import requests
import json
import os
from datetime import datetime

def fetch_futures_usdt_tickers():
    """
    Busca todos os pares de Binance Futures (USDT-margined) e retorna somente 
    os que terminam em 'USDT'. Ex.: { 'BTCUSDT': 28000.0, ... }
    """
    url = "https://fapi.binance.com/fapi/v1/ticker/price"
    response = requests.get(url)
    data = response.json()  # [{'symbol': 'BTCUSDT', 'price': '28000.0'}, ...]

    tickers = {}
    for item in data:
        symbol = item['symbol']
        # Filtrar símbolos que terminam em "USDT" (ex.: BTCUSDT, ETHUSDT, etc.)
        if symbol.endswith("USDT"):
            tickers[symbol] = float(item['price'])
    return tickers

def get_latest_futures_file():
    """
    Retorna o arquivo binance_futures_*.json mais recente, ou None se não houver nenhum.
    """
    files = [f for f in os.listdir('.') if f.startswith("binance_futures_") and f.endswith(".json")]
    if not files:
        return None
    # Ordenar pelo timestamp no nome do arquivo, do mais antigo p/ mais recente
    files_sorted = sorted(files, key=lambda x: x.replace("binance_futures_", "").replace(".json", ""))
    return files_sorted[-1]  # o último é o mais recente

def load_json_file(filepath):
    """
    Lê um arquivo JSON e retorna o dicionário correspondente.
    Se não existir ou der erro, retorna {}.
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
    Se existirem mais que 'limit' arquivos binance_futures_*.json,
    apaga o mais antigo (com base no timestamp do nome).
    """
    files = [f for f in os.listdir('.') if f.startswith("binance_futures_") and f.endswith(".json")]
    if len(files) > limit:
        # Ordenar do mais antigo p/ mais recente
        files_sorted = sorted(files, key=lambda x: x.replace("binance_futures_", "").replace(".json", ""))
        oldest = files_sorted[0]
        os.remove(oldest)
        print(f"Excluído o arquivo mais antigo: {oldest}")

def main():
    # 1. Carrega o arquivo binance_futures mais recente para comparar
    latest_file = get_latest_futures_file()
    old_data = load_json_file(latest_file) if latest_file else {}

    # 2. Busca tickers atuais de Binance Futures (USDT)
    new_data = fetch_futures_usdt_tickers()

    # 3. Determina quais são os tickers "novos" (presentes agora, mas não antes)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_tickers_list = []
    for symbol, price in new_data.items():
        if symbol not in old_data:
            new_tickers_list.append({
                "symbol": symbol,
                "price": price,
                "detected_at": now_str
            })

    # 4. Gera arquivo novo_binance_futures.json com esses tickers novos
    diff_output = {
        "script_run_at": now_str,
        "new_tickers": new_tickers_list
    }
    save_json_file(diff_output, "novo_binance_futures.json")

    # 5. Salva dados atuais em um arquivo binance_futures_YYYY-MM-DD_HH-MM-SS.json
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    futures_filename = f"binance_futures_{timestamp}.json"
    save_json_file(new_data, futures_filename)

    # 6. Mantém no máximo 2 arquivos binance_futures_*.json
    remove_oldest_if_exceeds(limit=2)

if __name__ == "__main__":
    main()
