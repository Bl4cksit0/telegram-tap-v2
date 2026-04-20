import os
import re
from datetime import datetime
from dotenv import load_dotenv
from pyrogram import Client, filters

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

@app.on_message(filters.chat(GROUP))
async def leer_mensaje(client, message):
    hora   = datetime.now().strftime("%H:%M:%S")
    nombre = message.from_user.first_name if message.from_user else "Desconocido"
    texto  = message.text or message.caption or "(sin texto)"

    if es_tarea(texto):
        numero = extraer_numero_tarea(texto)
        url    = extraer_url(texto)

        print(f"\n{'='*40}")
        print(f"  *** TAREA #{numero} DETECTADA [{hora}] ***")
        if url:
            print(f"  URL: {url}")
        print(f"{'='*40}")
        print(texto)
        print(f"{'='*40}\n")

        aviso = f"Tarea #{numero} detectada\n{url}" if url else f"Tarea #{numero} detectada\n(sin URL)"
        await client.send_message(BOT_DEST, aviso)
    else:
        print(f"[{hora}] {nombre}: {texto}")

print("Escuchando mensajes en vivo... (Ctrl+C para salir)")
app.run()
