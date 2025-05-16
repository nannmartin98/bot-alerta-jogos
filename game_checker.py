import requests
import datetime
import time
from config import API_TOKEN, TELEGRAM_CHAT_ID
from telegram_alert import send_telegram_message

HEADERS = {'X-Auth-Token': API_TOKEN}

campeonatos = {
    "WC": "Copa do Mundo",
    "CL": "Champions League",
    "BL1": "Bundesliga",
    "DED": "Eredivisie",
    "BSA": "Brasileirão Série A",
    "PD": "La Liga",
    "FL1": "Ligue 1",
    "ELC": "Championship",
    "PPL": "Primeira Liga",
    "EC": "Euro",
    "SA": "Serie A",
    "PL": "Premier League"
}

def get_scheduled_matches(competition_code):
    url = f"https://api.football-data.org/v4/competitions/{competition_code}/matches?status=SCHEDULED"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return data['matches']

def get_standings(competition_code):
    url = f"https://api.football-data.org/v4/competitions/{competition_code}/standings"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return data['standings'][0]['table']

def get_current_matchday(competition_code):
    url = f"https://api.football-data.org/v4/competitions/{competition_code}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return data['currentSeason']['currentMatchday']

def find_team_position(standings, team_name):
    for team in standings:
        if team['team']['name'] == team_name:
            return team['position'], team['points']
    return None, None

def is_important_match(match, standings, current_round):
    today = datetime.datetime.now().date()
    match_date = datetime.datetime.fromisoformat(match['utcDate'].replace("Z", "+00:00")).date()
    if match_date != today:
        return False

    home_team = match['homeTeam']['name']
    away_team = match['awayTeam']['name']

    pos_home, pts_home = find_team_position(standings, home_team)
    pos_away, pts_away = find_team_position(standings, away_team)

    if None in (pos_home, pos_away):
        return False

    zona_rebaixamento = len(standings) - 2
    zona_europa = 6
    zona_titulo = 1

    def perto_da_zona(pontos, zona_posicao):
        if zona_posicao <= 3:
            return pos_home <= zona_posicao + 2
        return abs(pos_home - zona_posicao) <= 2

    importante_home = (
        pos_home >= zona_rebaixamento or
        pos_home <= zona_europa or
        pos_home <= zona_titulo
    )

    importante_away = (
        pos_away >= zona_rebaixamento or
        pos_away <= zona_europa or
        pos_away <= zona_titulo
    )

    return importante_home or (importante_home and importante_away)

def format_match_message(match, campeonato):
    data = datetime.datetime.fromisoformat(match['utcDate'].replace("Z", "+00:00"))
    data_br = data - datetime.timedelta(hours=3)  # Ajuste para fuso horário brasileiro
    data_str = data_br.strftime("%d/%m/%Y %H:%M")
    return f"🔥 Jogo importante em {campeonato}!\n{match['homeTeam']['name']} x {match['awayTeam']['name']}\n🕒 {data_str}"

def main():
    jogos_importantes = []

    for codigo, nome in campeonatos.items():
        try:
            print(f"🔍 Buscando jogos de {nome}...")

            partidas = get_scheduled_matches(codigo)
            time.sleep(6)  # Respeitar limite da API

            standings = get_standings(codigo)
            time.sleep(6)

            rodada_atual = get_current_matchday(codigo)
            time.sleep(6)

            for partida in partidas:
                if is_important_match(partida, standings, rodada_atual):
                    jogos_importantes.append((partida, nome))

        except Exception as e:
            print(f"Erro ao buscar dados de {codigo}: {e}")

    print(f"🔍 Total de jogos pré-live encontrados: {len(jogos_importantes)}")

    for match, campeonato in jogos_importantes:
        mensagem = format_match_message(match, campeonato)
        send_telegram_message(mensagem)

if __name__ == "__main__":
    main()