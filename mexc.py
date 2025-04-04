import requests
import json
import os
from datetime import datetime

def fetch_mexc_spot_tickers():
    """
    Faz uma requisição ao endpoint de Ticker Spot da MEXC.
    URL: https://www.mexc.com/open/api/v2/market/ticker
    
    Resposta típica:
    {
      "code": 200,
      "data": [
        {
          "symbol": "BTC_USDT",
          "volume": "472.866131",
          "last": "22171.66",
          ...
        },
        ...
      ]
    }
    
    Retorna um dicionário no formato:
        { "BTC_USDT": 22171.66, "ETH_USDT": 1600.0, ... }
    """
    url = "https://www.mexc.com/open/api/v2/market/ticker"
    response = requests.get(url)
    data = response.json()
    
    # Verifica se code == 200 (sucesso)
    if data.get("code") != 200:
        raise Exception(f"Erro ao buscar dados Spot MEXC: {data}")
    
    tickers_dict = {}
    for item in data.get("data", []):
        symbol = item["symbol"]  # Ex: "BTC_USDT"
        last_str = item["last"]  # Ex: "22171.66"
        try:
            last_price = float(last_str)
            tickers_dict[symbol] = last_price
        except (ValueError, TypeError):
            pass
    
    return tickers_dict

def get_latest_mexc_spot_file():
    """
    Retorna o nome do arquivo mais recente que comece com 'mexc_spot_'
    e termine em '.json'. Se não existir, retorna None.
    """
    files = [f for f in os.listdir('.') if f.startswith("mexc_spot_") and f.endswith(".json")]
    if not files:
        return None
    # Ordenar do mais antigo para o mais recente
    files_sorted = sorted(files, key=lambda x: x.replace("mexc_spot_", "").replace(".json", ""))
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
    Se existirem mais do que 'limit' arquivos que comecem com 'mexc_spot_',
    remove o mais antigo (com base no timestamp no nome).
    """
    files = [f for f in os.listdir('.') if f.startswith("mexc_spot_") and f.endswith(".json")]
    if len(files) > limit:
        files_sorted = sorted(files, key=lambda x: x.replace("mexc_spot_", "").replace(".json", ""))
        oldest = files_sorted[0]
        os.remove(oldest)
        print(f"Excluído o arquivo mais antigo: {oldest}")

def main():
    try:
        # 1. Pega o arquivo mais recente (para comparação)
        latest_file = get_latest_mexc_spot_file()
        old_data = load_json_file(latest_file) if latest_file else {}

        # 2. Busca dados atuais
        new_data = fetch_mexc_spot_tickers()

        # 3. Verifica símbolos novos (não presentes no arquivo anterior)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_tickers_list = []
        for symbol, price in new_data.items():
            if symbol not in old_data:
                new_tickers_list.append({
                    "symbol": symbol,
                    "price": price,
                    "detected_at": now_str
                })

        # 4. Gera 'novo_mexc_spot.json' com símbolos recém-detectados
        diff_output = {
            "script_run_at": now_str,
            "new_tickers": new_tickers_list
        }
        save_json_file(diff_output, "novo_mexc_spot.json")

        # 5. Salva todos os dados atuais em 'mexc_spot_YYYY-MM-DD_HH-MM-SS.json'
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        spot_filename = f"mexc_spot_{timestamp}.json"
        save_json_file(new_data, spot_filename)

        # 6. Mantém no máximo 2 arquivos
        remove_oldest_if_exceeds(limit=2)

    except Exception as e:
        print(f"Falha ao buscar Spot da MEXC: {e}")

if __name__ == "__main__":
    main()
