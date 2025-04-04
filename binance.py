import requests
import json
import os
from datetime import datetime

def fetch_usdt_tickers_binance():
    """
    Busca todos os pares da Binance e retorna somente os que terminam em 'USDT'.
    Retorna um dicionário { 'BTCUSDT': 123.45, ... }.
    """
    url = "https://api.binance.com/api/v3/ticker/price"
    response = requests.get(url)
    data = response.json()

    tickers = {}
    for item in data:
        symbol = item['symbol']
        if symbol.endswith("USDT"):
            tickers[symbol] = float(item['price'])
    return tickers

def get_latest_spot_file():
    """
    Retorna o nome do arquivo 'binance_spot_*.json' mais recente.
    Caso não exista nenhum, retorna None.
    """
    files = [f for f in os.listdir('.') if f.startswith("binance_spot_") and f.endswith(".json")]
    if not files:
        return None
    # Ordena pelo trecho do nome que corresponde à data/hora, do mais antigo para o mais recente
    files_sorted = sorted(files, key=lambda x: x.replace("binance_spot_", "").replace(".json", ""))
    return files_sorted[-1]  # o último é o mais recente

def load_json_file(filepath):
    """
    Lê um arquivo JSON e retorna o dicionário correspondente.
    Se o arquivo não existir ou ocorrer erro de leitura, retorna {}.
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
    Salva o dicionário `data` em um arquivo JSON com indentação.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Arquivo '{filepath}' criado com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar arquivo {filepath}: {e}")

def remove_oldest_if_exceeds(limit=2):
    """
    Se existirem mais que 'limit' arquivos binance_spot_*.json,
    apaga o mais antigo (com base no timestamp no nome).
    """
    files = [f for f in os.listdir('.') if f.startswith("binance_spot_") and f.endswith(".json")]
    if len(files) > limit:
        files_sorted = sorted(files, key=lambda x: x.replace("binance_spot_", "").replace(".json", ""))
        oldest = files_sorted[0]
        os.remove(oldest)
        print(f"Excluído o arquivo mais antigo: {oldest}")

def main():
    # 1. Carrega o arquivo binance_spot mais recente, para comparar
    latest_file = get_latest_spot_file()
    old_data = load_json_file(latest_file) if latest_file else {}

    # 2. Busca tickers atuais da Binance (apenas USDT)
    new_data = fetch_usdt_tickers_binance()

    # 3. Determina quais são os tickers "novos" (presentes agora e não existentes anteriormente)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_tickers_list = []
    for symbol, price in new_data.items():
        if symbol not in old_data:
            new_tickers_list.append({
                "symbol": symbol,
                "price": price,
                "detected_at": now_str
            })

    # 4. Gera arquivo novo_binance_spot.json com esses tickers novos (se houver)
    diff_output = {
        "script_run_at": now_str,
        "new_tickers": new_tickers_list
    }
    save_json_file(diff_output, "novo_binance_spot.json")

    # 5. Salva os dados atuais em um arquivo datado para histórico
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    spot_filename = f"binance_spot_{timestamp}.json"
    save_json_file(new_data, spot_filename)

    # 6. Mantém no máximo 2 arquivos datados binance_spot_*.json
    remove_oldest_if_exceeds(limit=2)

if __name__ == "__main__":
    main()
