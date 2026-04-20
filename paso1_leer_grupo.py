import os
import re
from datetime import datetime
from dotenv import load_dotenv
from pyrogram import Client, filters, idle

load_dotenv()

API_ID   = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
PHONE    = os.environ["PHONE"]
GROUP    = os.environ["GROUP"]
BOT_DEST = "ThorBcKBot"

DIGIT_EMOJI = {
    "0️⃣": "0", "1️⃣": "1", "2️⃣": "2", "3️⃣": "3", "4️⃣": "4",
    "5️⃣": "5", "6️⃣": "6", "7️⃣": "7", "8️⃣": "8", "9️⃣": "9",
}

app = Client("sesion_v2", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE)

def extraer_numero_tarea(texto):
    for emoji, digito in DIGIT_EMOJI.items():
        texto = texto.replace(emoji, digito)
    match = re.search(r"\b(\d{1,3})\b", texto[:50])
    return match.group(1) if match else "?"

def extraer_url(texto):
    match = re.search(r"https?://[^\s]+", texto)
    return match.group(0) if match else None

def es_tarea(texto):
    tiene_lista   = bool(re.search(r"1\.", texto))
    tiene_youtube = "youtube" in texto.lower() or "búsqueda" in texto.lower() or "busqueda" in texto.lower()
    tiene_captura = "captura" in texto.lower()
    return tiene_lista and (tiene_youtube or tiene_captura)

async def procesar_tarea(client, texto):
    numero = extraer_numero_tarea(texto)
    url    = extraer_url(texto)

    print(f"\n{'='*40}")
    print(f"  *** TAREA #{numero} DETECTADA ***")
    if url:
        print(f"  URL: {url}")
    print(f"{'='*40}\n")

    aviso = f"Tarea #{numero} detectada\n{url}" if url else f"Tarea #{numero} detectada\n(sin URL)"
    try:
        await client.send_message(BOT_DEST, aviso)
        print(f"  [OK] Mensaje enviado a @{BOT_DEST}")
    except Exception as e:
        print(f"  [ERROR] No se pudo enviar a @{BOT_DEST}: {e}")

@app.on_message(filters.chat(GROUP))
async def leer_mensaje(client, message):
    hora   = datetime.now().strftime("%H:%M:%S")
    nombre = message.from_user.first_name if message.from_user else "Desconocido"
    texto  = message.text or message.caption or "(sin texto)"

    print(f"[LIVE {hora}] {nombre}: {texto}")
    print(f"  [DEBUG] es_tarea={es_tarea(texto)}")

    if es_tarea(texto):
        await procesar_tarea(client, texto)

async def main():
    await app.start()
    async for _ in app.get_dialogs():
        break

    limite = input("¿Cuántos mensajes del historial revisar? (50-500): ").strip()
    limite = max(50, min(500, int(limite) if limite.isdigit() else 100))

    print(f"\nRevisando los últimos {limite} mensajes del historial...")
    async for msg in app.get_chat_history(GROUP, limit=limite):
        texto = msg.text or msg.caption or ""
        if not texto:
            continue
        fecha = msg.date.strftime("%Y-%m-%d %H:%M")
        nombre = msg.from_user.first_name if msg.from_user else "Desconocido"
        print(f"[{fecha}] {nombre}: {texto[:80]}")
        if es_tarea(texto):
            await procesar_tarea(app, texto)

    print("\nHistorial revisado. Escuchando mensajes en vivo... (Ctrl+C para salir)")
    await idle()
    await app.stop()

app.run(main())
