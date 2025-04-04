import requests
import json
import os
from datetime import datetime

def fetch_bitget_spot_tickers():
    """
    Faz uma requisição à API de Spot da Bitget para obter todos os tickers e seus preços atuais.
    Retorna um dicionário no formato: { "BTCUSDT_SPBL": float(preco), ... }
    """
    url = "https://api.bitget.com/api/spot/v1/market/tickers"
    response = requests.get(url)
    data = response.json()

    # Verifica se o código de retorno é "00000" (sucesso)
    if data.get("code") != "00000":
        raise Exception(f"Erro ao buscar dados da Bitget Spot: {data.get('msg')}")

    tickers_dict = {}
    for item in data["data"]:
        symbol = item["symbol"]           # Ex: "BTCUSDT_SPBL"
        price = float(item["close"])      # converte 'close' de string para float
        tickers_dict[symbol] = price

    return tickers_dict

def get_latest_bitget_spot_file():
    """
    Retorna o nome do arquivo mais recente que começa com 'bitget_spot_' e termina em '.json'.
    Caso não exista nenhum, retorna None.
    """
    files = [f for f in os.listdir('.') if f.startswith("bitget_spot_") and f.endswith(".json")]
    if not files:
        return None
    # Ordena pelo timestamp embutido no nome (do mais antigo ao mais recente)
    files_sorted = sorted(files, key=lambda x: x.replace("bitget_spot_", "").replace(".json", ""))
    return files_sorted[-1]  # último = mais recente

def load_json_file(filepath):
    """
    Lê um arquivo JSON e retorna o dicionário correspondente.
    Se o arquivo não existir ou der erro, retorna {}.
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
    Se existirem mais do que 'limit' arquivos no padrão 'bitget_spot_*.json',
    remove o mais antigo (com base no timestamp no nome).
    """
    files = [f for f in os.listdir('.') if f.startswith("bitget_spot_") and f.endswith(".json")]
    if len(files) > limit:
        files_sorted = sorted(files, key=lambda x: x.replace("bitget_spot_", "").replace(".json", ""))
        oldest = files_sorted[0]
        os.remove(oldest)
        print(f"Excluído o arquivo mais antigo: {oldest}")

def main():
    # 1. Carrega o arquivo bitget_spot mais recente (para comparar)
    latest_file = get_latest_bitget_spot_file()
    old_data = load_json_file(latest_file) if latest_file else {}

    # 2. Faz a requisição atual à API (todos os tickers Spot)
    new_data = fetch_bitget_spot_tickers()

    # 3. Verifica quais são os símbolos "novos" (que não existiam no arquivo anterior)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_tickers_list = []
    for symbol, price in new_data.items():
        if symbol not in old_data:
            new_tickers_list.append({
                "symbol": symbol,
                "price": price,
                "detected_at": now_str
            })

    # 4. Salva a lista de novos tickers em 'novo_bitget_spot.json'
    diff_output = {
        "script_run_at": now_str,
        "new_tickers": new_tickers_list
    }
    save_json_file(diff_output, "novo_bitget_spot.json")

    # 5. Salva todos os dados atuais em 'bitget_spot_YYYY-MM-DD_HH-MM-SS.json'
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    spot_filename = f"bitget_spot_{timestamp}.json"
    save_json_file(new_data, spot_filename)

    # 6. Mantém no máximo 2 arquivos bitget_spot_*.json (exclui o mais antigo se passar de 2)
    remove_oldest_if_exceeds(limit=2)

if __name__ == "__main__":
    main()
