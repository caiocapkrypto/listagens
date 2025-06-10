import os
import time
import json
import requests
import subprocess

# Dados para envio de mensagem via Telegram
TOKEN = "8139155308:AAEvx1a077ngaxPNpXfUUaBuRxWUPnO8Zr0"
CHAT_ID = "-1002306200137" 

#Select capkrypto "-1002306200137"
# grupo de testes "-1002637091144"
# Mapeamento dos scripts e arquivos de "novos tickers"
# Assim sabemos de qual arquivo "novo_*.json" cada corretora gera
# e como rotular na mensagem (Spot ou Futures).
CORRETORAS = [
    {
        "script": "binance.py",
        "nome": "Binance (Spot)",
        "novo_file": "novo_binance_spot.json"
    },
    {
        "script": "binancef.py",
        "nome": "Binance (Futures)",
        "novo_file": "novo_binance_futures.json"
    },
    {
        "script": "bitget.py",
        "nome": "Bitget (Spot)",
        "novo_file": "novo_bitget_spot.json"
    },
    {
        "script": "bitgetf.py",
        "nome": "Bitget (Futures)",
        "novo_file": "novo_bitget_futures.json"
    },
    {
        "script": "bybit.py",
        "nome": "Bybit (Spot)",
        "novo_file": "novo_bybit_spot.json"
    },
    {
        "script": "bybitf.py",
        "nome": "Bybit (Futures)",
        "novo_file": "novo_bybit_futures.json"
    },
    {
        "script": "coinex.py",
        "nome": "CoinEx (Spot)",
        "novo_file": "novo_coinex_spot.json"
    },
    {
        "script": "htx.py",
        "nome": "HTX (Spot)",
        "novo_file": "novo_htx_spot.json"
    },
    {
        "script": "kucoin.py",
        "nome": "KuCoin (Spot)",
        "novo_file": "novo_kucoin_spot.json"
    },
    {
        "script": "mexc.py",
        "nome": "MEXC (Spot)",
        "novo_file": "novo_mexc_spot.json"
    },
    {
        "script": "mexcf.py",
        "nome": "MEXC (Futures)",
        "novo_file": "novo_mexc_futures.json"
    },
    {
        "script": "gateiof.py",
        "nome": "Gate (Futures)",
        "novo_file": "novo_gateio_futures.json"
    },
    {
        "script": "htxf.py",
        "nome": "HTX (Futures)",
        "novo_file": "novo_htx_futures.json"
    }

]

def run_xrun():
    """
    Executa o xrun.py (que roda todos os scripts das corretoras).
    """
    base_dir = os.path.dirname(os.path.abspath(__file__)) #pega a pasta deste arquivo
    xrun_path = os.path.join(base_dir, "xrun.py") #monta o caminho completo
    try:
        subprocess.run(["python3", xrun_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha ao executar xrun.py: {e}")
        
def load_new_tickers_file(filepath):
    """
    Carrega o arquivo JSON "novo_*.json" e retorna o dicionário correspondente.
    Formato típico esperado:
      {
        "script_run_at": "...",
        "new_tickers": [
          { "symbol": "BTCUSDT", "price": 25000, "detected_at": "2025-03-26 15:30:00" },
          ...
        ]
      }
    Se o arquivo não existir ou estiver vazio, retorna None.
    """
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"[ERRO] Não foi possível ler {filepath}: {e}")
        return None

def send_message_to_telegram(token, chat_id, text):
    """
    Envia uma mensagem de texto para o chat especificado via Telegram Bot API.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code != 200:
            print("[ERRO] Falha no envio de mensagem:", resp.text)
        else:
            print("[OK] Mensagem enviada ao Telegram.")
    except Exception as e:
        print(f"[ERRO] Exceção ao enviar mensagem Telegram: {e}")

def build_message(corretora_nome, new_tickers):
    """
    Monta a mensagem em português, adaptando singular/plural para 'ticker'/'tickers'.
    Exemplo de saída se for 1 ticker:
      "Binance (Spot) acaba de registrar o ticker: BTCUSDT (Preço: 25000.0)."
    Se forem vários:
      "Binance (Spot) acaba de registrar os tickers: BTCUSDT (25000.0), ETHUSDT (1700.0)."
    """
    count = len(new_tickers)
    if count == 1:
        ticker_info = new_tickers[0]
        symbol = ticker_info["symbol"]
        price = ticker_info["price"]
        message = (
            f"🚨{corretora_nome} acaba de registrar o ticker: {symbol} (Preço: {price})."
        )
    else:
        # Se há vários, gera uma lista "SYMBOL (PRICE)" para cada
        list_str = ", ".join([f"{t['symbol']} ({t['price']})" for t in new_tickers])
        message = (
            f"{corretora_nome} acaba de registrar os tickers: {list_str}."
        )
    return message

def check_and_send_new_tickers():
    """
    Para cada corretora, carrega o arquivo de novos tickers, se houver,
    envia a mensagem para o Telegram e exclui o arquivo.
    """
    for entry in CORRETORAS:
        nome_corretora = entry["nome"]
        new_file = entry["novo_file"]

        data = load_new_tickers_file(new_file)
        if data and "new_tickers" in data:
            new_list = data["new_tickers"]
            if len(new_list) > 0:
                # Monta e envia a mensagem
                msg = build_message(nome_corretora, new_list)
                send_message_to_telegram(TOKEN, CHAT_ID, msg)

            # Exclui o arquivo de novos tickers
            try:
                os.remove(new_file)
            except Exception as e:
                print(f"[ERRO] Falha ao excluir {new_file}: {e}")

def main():
    try:
        while True:
            # 1) Executa xrun.py (roda todos os scripts de corretoras)
            run_xrun()

            # 2) Verifica arquivos de novos tickers e envia mensagens
            check_and_send_new_tickers()

            # 3) Aguarda 15 minutos (900 segundos) e repete
            print("Aguardando 5 minutos para a próxima execução...\n")
            time.sleep(300)  # 15 * 60

    except KeyboardInterrupt:
        print("Execução interrompida pelo usuário.")

if __name__ == "__main__":
    main()
