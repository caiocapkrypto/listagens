import requests
import json
import os
from datetime import datetime

def fetch_bybit_spot_tickers_v5():
    """
    Faz uma chamada à API Bybit (v5) para buscar tickers Spot.
    Retorna um dicionário { "BTCUSDT": 34500.0, ... }.
    """
    url = "https://api.bybit.com/v5/market/tickers?category=spot"
    resp = requests.get(url)

    # Se quiser debug:
    # print("Status code:", resp.status_code)
    # print("Response text:", resp.text[:500])

    data = resp.json()
    if data.get("retCode") != 0:
        raise Exception(f"API Bybit v5 (Spot) erro: {data.get('retMsg')}")

    tickers_dict = {}
    list_spot = data["result"].get("list", [])
    for item in list_spot:
        symbol = item["symbol"]            # Ex.: "BTCUSDT"
        last_price_str = item["lastPrice"] # Ex.: "34500"
        tickers_dict[symbol] = float(last_price_str)
    
    return tickers_dict

def get_latest_bybit_spot_file():
    """
    Retorna o nome do arquivo mais recente que comece com 'bybit_spot_'
    e termine em '.json'. Se não existir, retorna None.
    """
    files = [f for f in os.listdir('.') if f.startswith("bybit_spot_") and f.endswith(".json")]
    if not files:
        return None
    # Ordenar pelo timestamp no nome, do mais antigo p/ mais recente
    files_sorted = sorted(files, key=lambda x: x.replace("bybit_spot_", "").replace(".json", ""))
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
    Se existirem mais que 'limit' arquivos que comecem com 'bybit_spot_',
    apaga o mais antigo (com base no timestamp no nome).
    """
    files = [f for f in os.listdir('.') if f.startswith("bybit_spot_") and f.endswith(".json")]
    if len(files) > limit:
        files_sorted = sorted(files, key=lambda x: x.replace("bybit_spot_", "").replace(".json", ""))
        oldest = files_sorted[0]
        os.remove(oldest)
        print(f"Excluído o arquivo mais antigo: {oldest}")

def main():
    # 1. Carrega o arquivo bybit_spot mais recente (para comparar)
    latest_file = get_latest_bybit_spot_file()
    old_data = load_json_file(latest_file) if latest_file else {}

    # 2. Busca dados atuais (Spot) da Bybit
    new_data = fetch_bybit_spot_tickers_v5()

    # 3. Verifica quais símbolos são novos
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_tickers_list = []
    for symbol, price in new_data.items():
        if symbol not in old_data:
            new_tickers_list.append({
                "symbol": symbol,
                "price": price,
                "detected_at": now_str
            })

    # 4. Cria o arquivo 'novo_bybit_spot.json' com os tickers detectados
    diff_output = {
        "script_run_at": now_str,
        "new_tickers": new_tickers_list
    }
    save_json_file(diff_output, "novo_bybit_spot.json")

    # 5. Salva os dados atuais em 'bybit_spot_YYYY-MM-DD_HH-MM-SS.json'
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    spot_filename = f"bybit_spot_{timestamp}.json"
    save_json_file(new_data, spot_filename)

    # 6. Mantém no máximo 2 arquivos de histórico 'bybit_spot_*.json'
    remove_oldest_if_exceeds(limit=2)

if __name__ == "__main__":
    main()
