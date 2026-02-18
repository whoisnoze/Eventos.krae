import asyncio
from playwright.async_api import async_playwright
from telegram import Bot
from telegram.constants import ParseMode

# --- CONFIGURACIÓN ---
TOKEN = ''
CHAT_ID = ''
URL = ""

async def extraer_agenda():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print("🌐 Accediendo a Marca...")
            await page.goto(URL, wait_until="networkidle")
            
            try:
                await page.wait_for_selector("#didomi-notice-agree-button", timeout=3000)
                await page.click("#didomi-notice-agree-button")
            except:
                pass

            await page.wait_for_timeout(2000)
            
            # Buscamos los eventos
            eventos_raw = await page.query_selector_all("li[class*='event'], div[class*='event']")
            
            lista_final = []
            for ev in eventos_raw:
                texto = await ev.inner_text()
                # Limpiamos y eliminamos líneas vacías
                lineas = [l.strip() for l in texto.split('\n') if l.strip()]
                
                # Basado en tu última salida, el formato es:
                # [DEPORTE, HORA, TITULO, SUBTITULO (opcional), CANAL]
                if len(lineas) >= 4:
                    deporte = lineas[0].upper()
                    hora = lineas[1]
                    evento = lineas[2]
                    detalle = lineas[3]
                    # El canal suele ser el último elemento
                    canal = lineas[-1]

                    # Emoji personalizado
                    emoji = "⚽" if "FÚTBOL" in deporte else "🏀" if "BALONCESTO" in deporte or "ENDESA" in deporte else "🎾" if "TENIS" in deporte or "ATP" in deporte else "🏎️" if "FÓRMULA" in deporte or "F1" in deporte else "🚴" if "CICLISMO" in deporte or "TOUR" in deporte else "🏆"
                    
                    # Construimos el mensaje con un diseño limpio
                    # Ejemplo: ⚽ 21:00 | Brujas - Atlético de Madrid
                    #          📺 Movistar Plus+ (CHAMPIONS LEAGUE)
                    linea = f"{emoji} *{hora}* | *{evento}*\n└ {detalle}\n📺 _{canal}_"
                    lista_final.append(linea)
            
            await browser.close()
            return "\n\n".join(lista_final[:25]) # Mandamos los 25 primeros
            
        except Exception as e:
            await browser.close()
            return f"❌ Error en la extracción: {e}"

async def enviar_telegram():
    print("🤖 Generando agenda para Telegram...")
    texto_agenda = await extraer_agenda()
    
    header = "📅 *AGENDA DEPORTIVA HOY* 📅\n"
    header += "" + "—"*15 + "\n\n"
    
    bot = Bot(token=TOKEN)
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=header + texto_agenda, 
        parse_mode=ParseMode.MARKDOWN
    )
    print("✅ Mensaje enviado!")

if __name__ == "__main__":
    asyncio.run(enviar_telegram())
