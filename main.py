# main.py

import schedule
import time
from game_checker import checar_jogos_flashscore

def executar_bot():
    print("🔄 Verificando jogos pré-live...")
    checar_jogos_flashscore()
    print("✅ Verificação concluída.\n")

# Agendar a execução a cada 15 minutos
schedule.every(15).minutes.do(executar_bot)

print("🤖 Bot MatchWin iniciado. Monitorando jogos a cada 15 minutos...\n")

# Loop contínuo
while True:
    schedule.run_pending()
    time.sleep(1)
