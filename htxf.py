import requests
import json
import os
from datetime import datetime

# Endpoint correto para HTX USDT-margined Futures – Get a Batch of Market Data Overview
HTX_FUTURES_API = "https://api.hbdm.com/linear-swap-ex/market/detail/batch_merged"

def fetch_htx_futures_tickers():
    """
    Faz requisição à API HTX USDT-margined (swap/perp) – Get a Batch of Market Data Overview.
    Retorna um dict { "BTCUSDT": 30000.0, ... } baseado em data['ticks'] e campo 'close'.
    """
    response = requests.get(HTX_FUTURES_API)
    response.raise_for_status()
    data = response.json()

    if data.get("status") != "ok":
        raise Exception(f"Erro na API HTX Futures: {data.get('err_msg', data)}")

    ticks = data.get("ticks", [])
    tickers = {}
    for item in ticks:
        raw = item.get("contract_code")        # ex: "BTC-USDT"
        price_str = item.get("close")          # ex: "4.65E-8"
        if not raw or price_str is None:
            continue
        symbol = raw.replace("-", "").upper()  # ex: "BTCUSDT"
        try:
            tickers[symbol] = float(price_str)
        except (ValueError, TypeError):
            # ignora se não converter
            continue

    return tickers

def get_latest_htx_futures_file():
    files = [f for f in os.listdir('.') if f.startswith("htx_futures_") and f.endswith(".json")]
    if not files:
        return None
    files_sorted = sorted(files, key=lambda x: x.replace("htx_futures_", "").replace(".json", ""))
    return files_sorted[-1]

def load_json_file(filepath):
    if not filepath or not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_json_file(data, filepath):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Arquivo '{filepath}' criado com sucesso!")

def remove_oldest_if_exceeds(limit=2):
    files = [f for f in os.listdir('.') if f.startswith("htx_futures_") and f.endswith(".json")]
    if len(files) > limit:
        files_sorted = sorted(files, key=lambda x: x.replace("htx_futures_", "").replace(".json", ""))
        os.remove(files_sorted[0])
        print(f"Excluído arquivo antigo: {files_sorted[0]}")

def main():
    # 1. Histórico anterior
    latest = get_latest_htx_futures_file()
    old_data = load_json_file(latest) if latest else {}

    # 2. Dados atuais
    new_data = fetch_htx_futures_tickers()

    # 3. Identifica símbolos novos
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_tickers = [
        {"symbol": s, "price": p, "detected_at": now}
        for s, p in new_data.items() if s not in old_data
    ]

    # 4. Salva diffs
    save_json_file({"script_run_at": now, "new_tickers": new_tickers}, "novo_htx_futures.json")

    # 5. Salva snapshot
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    snapshot = f"htx_futures_{ts}.json"
    save_json_file(new_data, snapshot)

    # 6. Limita histórico
    remove_oldest_if_exceeds(limit=2)

if __name__ == "__main__":
    main()
