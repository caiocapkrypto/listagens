import requests
import json
import os
from datetime import datetime

def fetch_kucoin_spot_tickers():
    """
    Faz uma requisição ao endpoint 'GET /api/v1/market/allTickers' para obter
    todos os tickers de Spot da KuCoin.
    
    Retorna um dicionário no formato:
        { "KCS-BTC": 0.00012, "ETH-BTC": 0.077, ... }
    """
    url = "https://api.kucoin.com/api/v1/market/allTickers"
    response = requests.get(url)
    data = response.json()
    
    # A KuCoin costuma retornar "code" = "200000" para sucesso
    if data.get("code") != "200000":
        raise Exception(f"Erro ao buscar dados da KuCoin: {data.get('msg', data)}")
    
    tickers_dict = {}
    # Em data["data"]["ticker"] vem uma lista de dicionários
    ticker_list = data.get("data", {}).get("ticker", [])
    
    for item in ticker_list:
        symbol = item["symbol"]        # Ex: "KCS-BTC"
        last_price_str = item["last"]  # Ex: "0.00012"
        
        try:
            last_price = float(last_price_str)
            tickers_dict[symbol] = last_price
        except ValueError:
            pass
    
    return tickers_dict

def get_latest_kucoin_spot_file():
    """
    Retorna o nome do arquivo mais recente que comece com 'kucoin_spot_'
    e termine em '.json'. Se não existir, retorna None.
    """
    files = [f for f in os.listdir('.') if f.startswith("kucoin_spot_") and f.endswith(".json")]
    if not files:
        return None
    # Ordena do mais antigo ao mais recente
    files_sorted = sorted(files, key=lambda x: x.replace("kucoin_spot_", "").replace(".json", ""))
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
    Se existirem mais do que 'limit' arquivos que comecem com 'kucoin_spot_',
    remove o mais antigo (com base no timestamp no nome).
    """
    files = [f for f in os.listdir('.') if f.startswith("kucoin_spot_") and f.endswith(".json")]
    if len(files) > limit:
        files_sorted = sorted(files, key=lambda x: x.replace("kucoin_spot_", "").replace(".json", ""))
        oldest = files_sorted[0]
        os.remove(oldest)
        print(f"Excluído o arquivo mais antigo: {oldest}")

def main():
    try:
        # 1. Encontra o arquivo kucoin_spot mais recente (para comparar)
        latest_file = get_latest_kucoin_spot_file()
        old_data = load_json_file(latest_file) if latest_file else {}

        # 2. Busca dados atuais de Spot na KuCoin
        new_data = fetch_kucoin_spot_tickers()

        # 2.1. Remover especificamente "VRA-USDT" do dicionário, se houver:
        if "VRA-USDT" in new_data:
            new_data.pop("VRA-USDT")
            print("Removido VRA-USDT do resultado atual.")

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

        # 4. Cria 'novo_kucoin_spot.json' com os símbolos recém-detectados
        diff_output = {
            "script_run_at": now_str,
            "new_tickers": new_tickers_list
        }
        save_json_file(diff_output, "novo_kucoin_spot.json")

        # 5. Salva os dados atuais em 'kucoin_spot_YYYY-MM-DD_HH-MM-SS.json'
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        spot_filename = f"kucoin_spot_{timestamp}.json"
        save_json_file(new_data, spot_filename)

        # 6. Mantém no máximo 2 arquivos de histórico
        remove_oldest_if_exceeds(limit=2)

    except Exception as e:
        print(f"Erro ao buscar dados da KuCoin Spot: {e}")

if __name__ == "__main__":
    main()
