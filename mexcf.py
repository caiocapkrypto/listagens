import requests
import json
import os
from datetime import datetime

def fetch_mexc_futures_tickers():
    """
    Faz uma requisição ao endpoint de Futuros (Contract) da MEXC.
    URL: https://contract.mexc.com/api/v1/contract/ticker
    
    A resposta típica é algo do tipo:
    {
       "code": 200,
       "data": [
         {
           "contractId": 710,
           "symbol": "GOMINING_USDT",
           "lastPrice": 0.4905,
           ...
         },
         ...
       ]
    }
    
    Retorna um dicionário no formato:
       { "GOMINING_USDT": 0.4905, ... }
    """
    url = "https://contract.mexc.com/api/v1/contract/ticker"
    response = requests.get(url)

    # Debug (opcional):
    # print("Status code:", response.status_code)
    # print("Response snippet:", response.text[:300], "...")

    data = response.json()

    if not isinstance(data, dict):
        raise Exception(f"Resposta não é um dicionário! Retornado: {data}")

    ticker_list = data.get("data")
    if ticker_list is None:
        raise Exception(f"Chave 'data' não encontrada na resposta da MEXC: {data}")

    # Se for um único objeto, transforma em lista
    if isinstance(ticker_list, dict):
        ticker_list = [ticker_list]
    elif not isinstance(ticker_list, list):
        raise Exception(f"Formato inesperado em data['data']: {ticker_list}")

    tickers_dict = {}
    for item in ticker_list:
        symbol = item["symbol"]           # Ex.: "GOMINING_USDT"
        last_price = item["lastPrice"]    # Ex.: 0.4905

        try:
            last_price = float(last_price)
            tickers_dict[symbol] = last_price
        except (ValueError, TypeError):
            continue

    return tickers_dict

def get_latest_mexc_futures_file():
    """
    Retorna o nome do arquivo mais recente que comece com 'mexc_futures_'
    e termine em '.json'. Se não existir, retorna None.
    """
    files = [f for f in os.listdir('.') if f.startswith("mexc_futures_") and f.endswith(".json")]
    if not files:
        return None
    # Ordena do mais antigo para o mais recente
    files_sorted = sorted(files, key=lambda x: x.replace("mexc_futures_", "").replace(".json", ""))
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
    Se existirem mais do que 'limit' arquivos que comecem com 'mexc_futures_',
    apaga o mais antigo (com base no timestamp no nome).
    """
    files = [f for f in os.listdir('.') if f.startswith("mexc_futures_") and f.endswith(".json")]
    if len(files) > limit:
        files_sorted = sorted(files, key=lambda x: x.replace("mexc_futures_", "").replace(".json", ""))
        oldest = files_sorted[0]
        os.remove(oldest)
        print(f"Excluído o arquivo mais antigo: {oldest}")

def main():
    try:
        # 1. Carrega o arquivo mexc_futures mais recente (para comparar)
        latest_file = get_latest_mexc_futures_file()
        old_data = load_json_file(latest_file) if latest_file else {}

        # 2. Busca dados atuais
        new_data = fetch_mexc_futures_tickers()

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

        # 4. Cria 'novo_mexc_futures.json' com os símbolos recém-detectados
        diff_output = {
            "script_run_at": now_str,
            "new_tickers": new_tickers_list
        }
        save_json_file(diff_output, "novo_mexc_futures.json")

        # 5. Salva todos os dados atuais em 'mexc_futures_YYYY-MM-DD_HH-MM-SS.json'
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        futures_filename = f"mexc_futures_{timestamp}.json"
        save_json_file(new_data, futures_filename)

        # 6. Mantém no máximo 2 arquivos
        remove_oldest_if_exceeds(limit=2)

    except Exception as e:
        print(f"Falha ao buscar Futuros da MEXC: {e}")

if __name__ == "__main__":
    main()
