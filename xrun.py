import os
import subprocess

# Lista de scripts que você deseja executar
UPDATE_SCRIPTS = [
    "binance.py",
    "binancef.py",
    "bitget.py",
    "bitgetf.py",
    "bybit.py",
    "bybitf.py",
    "coinex.py",
    "htx.py",
    "kucoin.py",
    "mexc.py",
    "mexcf.py"
]

def run_all_scripts():
    """
    Executa cada script na lista UPDATE_SCRIPTS em sequência, utilizando subprocess.
    Caso algum script retorne código de erro, o log correspondente será exibido.
    """
    # Descobre o diretório atual deste arquivo (para encontrar os scripts)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    for script_name in UPDATE_SCRIPTS:
        script_path = os.path.join(base_dir, script_name)

        # Verifica se o script existe no diretório
        if not os.path.exists(script_path):
            print(f"[AVISO] Script {script_name} não encontrado em {script_path}. Ignorando.")
            continue

        print(f"==> Executando {script_name}...")

        # Executa o script via subprocess
        try:
            # Se quiser ver as saídas do script diretamente no console,
            # deixe capture_output=False, ou omita esse parâmetro.
            # Se quiser capturar as saídas para tratamento, use capture_output=True.
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"[OK] {script_name} executado com sucesso!")
                if result.stdout:
                    print("Saída do script:\n", result.stdout.strip())
            else:
                print(f"[ERRO] Falha ao executar {script_name}. Código de retorno: {result.returncode}")
                if result.stderr:
                    print("Mensagem de erro:\n", result.stderr.strip())

        except Exception as e:
            print(f"[EXCEÇÃO] Ocorreu um erro ao tentar executar {script_name}: {e}")

if __name__ == "__main__":
    run_all_scripts()
