import requests
from datetime import datetime, timezone
import pytz

TOKEN_TELEGRAM = ""
CHAT_ID = ""
API_KEY = ""

HEADERS = {
    "x-apisports-key": API_KEY,
    "Accept": "application/json"
}

# Diccionario
LIGAS_IMPORTANTES = {
    "La Liga": 140,
    "Segunda División": 141,
    "Copa del Rey": 143,
    "Supercopa de España": 556,
    
    "Champions League": 2,
    "Europa League": 3,

    "Premier League": 39,
    "Championship": 40,
    "FA Cup": 45,
    "EFL Cup": 48,

    "Bundesliga": 78,
    "2. Bundesliga": 79,
    "DFB-Pokal": 82,

    "Serie A": 135,
    "Serie B": 136,
    "Coppa Italia": 137,

    "Ligue 1": 61,
    "Ligue 2": 62,
    "Coupe de France": 66
}

LIGAS_BALONCESTO = {
    "ACB": 117,
    "NBA": 12
}

# Fecha
hoy = datetime.now().strftime("%Y-%m-%d")
madrid = pytz.timezone("Europe/Madrid")

# Eventos de futbol
def obtener_eventos_futbol():
    mensaje = "⚽ *Eventos de fútbol*\n\n"

    try:
        url = f"https://v3.football.api-sports.io/fixtures?date={hoy}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
    except Exception as e:
        print(f"Error al consultar la API: {e}")
        return "No se pudo consultar la API"

    eventos = data.get("response", [])
    if not eventos:
        return "No hay partidos hoy."

    for evento in eventos:
        fixture = evento.get("fixture")
        teams = evento.get("teams")
        league = evento.get("league")
        if not fixture or not teams or not league:
            continue

        # Filtrar solo por ligas asignadas
        if league.get("id") not in LIGAS_IMPORTANTES.values():
            continue

        # Convertir hora UTC a Madrid
        fecha_utc = datetime.fromisoformat(fixture["date"].replace("Z","+00:00"))
        hora_local = fecha_utc.astimezone(madrid).strftime("%H:%M")

        mensaje += f"{hora_local} | {league['name']}\n"
        mensaje += f"🆚 {teams['home']['name']} vs {teams['away']['name']}\n\n"

    return mensaje

# Eventos de Baloncesto
def obtener_eventos_balon():
    mensaje = "🏀 *Eventos de baloncesto hoy*\n\n"

    for liga_nombre, liga_id in LIGAS_BALONCESTO.items():
        params = {
            "league": liga_id,
            "season": 2026,
            "date": hoy
        }

        try:
            url = "https://v1.basketball.api-sports.io/fixtures"
            r = requests.get(url, headers=HEADERS, params=params, timeout=10)
            data = r.json()
        except Exception as e:
            print(f"Error consultando {liga_nombre}: {e}")
            continue

        eventos = data.get("response", [])
        if not eventos:
            continue

        for evento in eventos:
            fixture = evento.get("fixture")
            teams = evento.get("teams")
            if not fixture or not teams:
                continue

            # Convertir hora UTC a Madrid
            fecha_utc = datetime.fromisoformat(fixture["date"].replace("Z","+00:00"))
            hora_local = fecha_utc.astimezone(madrid).strftime("%H:%M")

            mensaje += f"{hora_local} | {liga_nombre}\n"
            mensaje += f"🆚 {teams['home']['name']} vs {teams['away']['name']}\n\n"

    return mensaje

# Eventos F1
def obtener_eventos_f1():
    mensaje = "🏎️ *Eventos de Formula 1*\n\n"

    try:
        url = "https://v1.formula-1.api-sports.io/races"
        params = {
            "season": 2026,
            "date": hoy,
            "timezone": "Europe/Madrid"
        }
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        data = r.json()
    except Exception as e:
        print(f"Error consultando F1: {e}")
        return "No se pudo consultar la API de F1"

    eventos = data.get("response", [])
    if not eventos:
        return "🏎️ No hay carreras de F1 hoy."

    for carrera in eventos:
        race = carrera.get("race")
        circuit = carrera.get("circuit")
        if not race or not circuit:
            continue

        # Hora de inicio ya viene en la API con timezone
        hora = race.get("date")

        mensaje += f"{hora} | {race['name']}\n"
        mensaje += f"📍 {circuit['name']}, {circuit['location']['city']}, {circuit['location']['country']}\n\n"


# MEnsaje de Telegram
def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    try:
        r = requests.post(url, data=payload)
        if r.status_code != 200:
            print(f"Error enviando mensaje: {r.text}")
    except Exception as e:
        print(f"Excepción al enviar mensaje: {e}")

# ---------- MAIN ----------
if __name__ == "__main__":
    msg_futbol = obtener_eventos_futbol()
    msg_balon = obtener_eventos_balon()
    msg_f1 = obtener_eventos_f1()
    msg_completo = "📅 *Calendario de hoy*\n\n" + msg_futbol + "\n" + msg_balon + "\n" + msg_f1
    enviar_telegram(msg_completo)
    print("Mensaje enviado a Telegram.")