import requests
import json
import os
from datetime import datetime

def fetch_htx_spot_tickers():
    """
    Faz uma requisição à API Spot da HTX (https://api.htx.com/market/tickers)
    para obter todos os tickers e seus preços atuais.

    Retorna um dicionário no formato:
        { "BTCUSDT": 29000.5, "ETHUSDT": 1850.3, ... }
    """
    url = "https://api.htx.com/market/tickers"
    response = requests.get(url)
    data = response.json()
    
    # Verifica se o campo 'status' é "ok"
    if data.get("status") != "ok":
        raise Exception(f"Erro na API HTX Spot: {data.get('err_msg', data)}")

    tickers_dict = {}
    # data["data"] deve ser uma lista de dicionários, cada um contendo "symbol", "close", etc.
    for item in data.get("data", []):
        symbol_raw = item["symbol"]      # ex: "btcusdt"
        last_price_str = item["close"]   # ex: "29000.5"

        # Converter símbolo para maiúsculo (opcional)
        symbol = symbol_raw.upper()      # ex.: "BTCUSDT"

        # Converter preço de string para float
        try:
            last_price = float(last_price_str)
            tickers_dict[symbol] = last_price
        except (ValueError, TypeError):
            continue
    
    return tickers_dict

def get_latest_htx_spot_file():
    """
    Retorna o arquivo mais recente que comece com 'htx_spot_'
    e termine em '.json'. Se não existir, retorna None.
    """
    files = [f for f in os.listdir('.') if f.startswith("htx_spot_") and f.endswith(".json")]
    if not files:
        return None
    # Ordenar do mais antigo para o mais recente
    files_sorted = sorted(files, key=lambda x: x.replace("htx_spot_", "").replace(".json", ""))
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
    Se existirem mais do que 'limit' arquivos que comecem com 'htx_spot_',
    remove o mais antigo (com base no timestamp no nome).
    """
    files = [f for f in os.listdir('.') if f.startswith("htx_spot_") and f.endswith(".json")]
    if len(files) > limit:
        files_sorted = sorted(files, key=lambda x: x.replace("htx_spot_", "").replace(".json", ""))
        oldest = files_sorted[0]
        os.remove(oldest)
        print(f"Excluído o arquivo mais antigo: {oldest}")

def main():
    try:
        # 1. Localiza o arquivo htx_spot mais recente (para comparar)
        latest_file = get_latest_htx_spot_file()
        old_data = load_json_file(latest_file) if latest_file else {}

        # 2. Busca dados atuais da HTX Spot
        new_data = fetch_htx_spot_tickers()

        # 3. Identifica símbolos novos (não presentes no arquivo anterior)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_tickers_list = []
        for symbol, price in new_data.items():
            if symbol not in old_data:
                new_tickers_list.append({
                    "symbol": symbol,
                    "price": price,
                    "detected_at": now_str
                })

        # 4. Cria 'novo_htx_spot.json' com os símbolos recém-detectados
        diff_output = {
            "script_run_at": now_str,
            "new_tickers": new_tickers_list
        }
        save_json_file(diff_output, "novo_htx_spot.json")

        # 5. Cria arquivo datado 'htx_spot_YYYY-MM-DD_HH-MM-SS.json'
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        spot_filename = f"htx_spot_{timestamp}.json"
        save_json_file(new_data, spot_filename)

        # 6. Mantém no máximo 2 arquivos htx_spot_*.json
        remove_oldest_if_exceeds(limit=2)

    except Exception as e:
        print(f"Erro ao buscar dados da HTX Spot: {e}")

if __name__ == "__main__":
    main()
