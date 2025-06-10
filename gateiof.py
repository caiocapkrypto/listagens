import requests
import json
import os
from datetime import datetime

def fetch_gateio_futures_tickers():
    """
    Faz requisição à API de Futuros USDT da Gate.io (v4) e retorna
    um dicionário { "BTC_USDT": 12345.6, ... }.
    """
    url = "https://api.gateio.ws/api/v4/futures/usdt/tickers"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    tickers = {}
    # cada item: {"contract": "BTC_USDT", "last": "12345.6", ...}
    for item in data:
        symbol = item.get("contract")
        last_str = item.get("last")
        try:
            tickers[symbol] = float(last_str)
        except (TypeError, ValueError):
            continue
    return tickers

def get_latest_gateio_futures_file():
    """
    Retorna o nome do arquivo mais recente 'gateio_futures_*.json', ou None.
    """
    files = [f for f in os.listdir('.') 
             if f.startswith("gateio_futures_") and f.endswith(".json")]
    if not files:
        return None
    files_sorted = sorted(
        files, 
        key=lambda x: x.replace("gateio_futures_", "").replace(".json", "")
    )
    return files_sorted[-1]

def load_json_file(filepath):
    """
    Lê um JSON e retorna dict, ou {} em caso de falha.
    """
    if not filepath or not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_json_file(data, filepath):
    """
    Salva dict em JSON com indentação.
    """
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Arquivo '{filepath}' criado com sucesso!")

def remove_oldest_if_exceeds(limit=2):
    """
    Se houver mais de `limit` arquivos 'gateio_futures_*.json', apaga o mais antigo.
    """
    files = [f for f in os.listdir('.') 
             if f.startswith("gateio_futures_") and f.endswith(".json")]
    if len(files) > limit:
        files_sorted = sorted(
            files, 
            key=lambda x: x.replace("gateio_futures_", "").replace(".json", "")
        )
        os.remove(files_sorted[0])
        print(f"Excluído arquivo antigo: {files_sorted[0]}")

def main():
    # 1. Carrega histórico anterior
    latest = get_latest_gateio_futures_file()
    old_data = load_json_file(latest) if latest else {}

    # 2. Busca dados atuais
    new_data = fetch_gateio_futures_tickers()

    # 3. Identifica novos símbolos
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_tickers = [
        {"symbol": s, "price": p, "detected_at": now_str}
        for s, p in new_data.items() if s not in old_data
    ]

    # 4. Salva diffs
    diff = {"script_run_at": now_str, "new_tickers": new_tickers}
    save_json_file(diff, "novo_gateio_futures.json")

    # 5. Salva snapshot com timestamp
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    snapshot = f"gateio_futures_{ts}.json"
    save_json_file(new_data, snapshot)

    # 6. Limita histórico
    remove_oldest_if_exceeds(limit=2)

if __name__ == "__main__":
    main()
