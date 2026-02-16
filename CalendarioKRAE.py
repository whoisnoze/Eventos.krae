import requests
import asyncio
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime

TOKEN = ""
CHAT_ID = ""
URL = ""



def obtener_eventos():
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, "html.parser")

    mensaje = "📅 *Eventos de hoy*\n\n"

    filas = soup.find_all("tr")  # Ajusta según la web

    for fila in filas:
        columnas = fila.find_all("td")
        if len(columnas) >= 5:
            hora = columnas[1].text.strip()
            deporte = columnas[2].text.strip()
            competicion = columnas[3].text.strip()
            partido = columnas[4].text.strip()

            # Emoji según el deporte
            deporte_lower = deporte.lower()
            if "fútbol" in deporte_lower:
                icono = "⚽"
            elif "tenis" in deporte_lower:
                icono = "🎾"
            elif "baloncesto" in deporte_lower or "basket" in deporte_lower:
                icono = "🏀"
            elif "f1" in deporte_lower or "formula 1" in deporte_lower:
                icono = "🏎️"
            elif "moto" in deporte_lower or "motociclismo" in deporte_lower:
                icono = "🏍️"
            else:
                icono = "🏆"

            mensaje += f"{icono} *{hora}* | {deporte}\n"
            mensaje += f"📌 {competicion}\n"
            mensaje += f"🆚 {partido}\n\n"

    return mensaje

async def enviar_telegram(mensaje):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=mensaje)


async def main():
    mensaje = obtener_eventos()

    if len(mensaje) > 20:  # evita enviar vacío
        await enviar_telegram(mensaje)
    else:
        print("No hay eventos hoy.")


if __name__ == "__main__":
    asyncio.run(main())











