import requests
import json
import os
from datetime import datetime

def fetch_coinex_spot_tickers():
    """
    Faz requisição ao endpoint /v1/market/ticker/all da CoinEx para obter todos os tickers Spot.
    
    Formato típico de resposta:
    {
      "code": 0,
      "data": {
        "date": 1688225435,
        "ticker": {
          "BTCUSDT": { "last": "30005.0", ... },
          "ETHUSDT": { "last": "1850.5", ... },
          ...
        }
      },
      "message": "Ok"
    }
    
    Retorna um dicionário no formato:
      {
        "BTCUSDT": 30005.0,
        "ETHUSDT": 1850.5,
        ...
      }
    """
    url = "https://api.coinex.com/v1/market/ticker/all"
    response = requests.get(url)
    data = response.json()
    
    # Verifica se "code" é 0 (sucesso)
    if data.get("code") != 0:
        raise Exception(f"Erro na API CoinEx: {data.get('message')}")
    
    # Acessa a seção "ticker"
    ticker_data = data.get("data", {}).get("ticker", {})
    if not ticker_data:
        raise Exception(f"Não foi possível encontrar dados de ticker na resposta: {data}")
    
    tickers_dict = {}
    # ticker_data é um dicionário: { "BTCUSDT": {"last": "...", ...}, "ETHUSDT": {...}, ... }
    for symbol, info in ticker_data.items():
        last_str = info.get("last")
        if not last_str:
            continue
        try:
            last_price = float(last_str)
            tickers_dict[symbol] = last_price
        except ValueError:
            pass
    
    return tickers_dict

def get_latest_coinex_spot_file():
    """
    Retorna o nome do arquivo mais recente que comece com 'coinex_spot_'
    e termine em '.json'. Se não existir, retorna None.
    """
    files = [f for f in os.listdir('.') if f.startswith("coinex_spot_") and f.endswith(".json")]
    if not files:
        return None
    # Ordenar do mais antigo para o mais recente
    files_sorted = sorted(files, key=lambda x: x.replace("coinex_spot_", "").replace(".json", ""))
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
    Se existirem mais do que 'limit' arquivos que comecem com 'coinex_spot_',
    remove o mais antigo (com base no timestamp no nome).
    """
    files = [f for f in os.listdir('.') if f.startswith("coinex_spot_") and f.endswith(".json")]
    if len(files) > limit:
        files_sorted = sorted(files, key=lambda x: x.replace("coinex_spot_", "").replace(".json", ""))
        oldest = files_sorted[0]
        os.remove(oldest)
        print(f"Excluído o arquivo mais antigo: {oldest}")

def main():
    try:
        # 1. Carrega o arquivo coinex_spot mais recente (para comparar)
        latest_file = get_latest_coinex_spot_file()
        old_data = load_json_file(latest_file) if latest_file else {}

        # 2. Busca dados atuais
        new_data = fetch_coinex_spot_tickers()

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

        # 4. Gera 'novo_coinex_spot.json' com os símbolos novos
        diff_output = {
            "script_run_at": now_str,
            "new_tickers": new_tickers_list
        }
        save_json_file(diff_output, "novo_coinex_spot.json")

        # 5. Salva os dados atuais em 'coinex_spot_YYYY-MM-DD_HH-MM-SS.json'
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        spot_filename = f"coinex_spot_{timestamp}.json"
        save_json_file(new_data, spot_filename)

        # 6. Mantém no máximo 2 arquivos de histórico
        remove_oldest_if_exceeds(limit=2)

    except Exception as e:
        print(f"Erro ao buscar dados da CoinEx Spot: {e}")

if __name__ == "__main__":
    main()
