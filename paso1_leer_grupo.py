import os
from datetime import datetime
from dotenv import load_dotenv
from pyrogram import Client, filters

load_dotenv()

API_ID   = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
PHONE    = os.environ["PHONE"]
GROUP    = os.environ["GROUP"]

app = Client("sesion_v2", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE)

@app.on_message(filters.chat(GROUP))
async def leer_mensaje(client, message):
    hora  = datetime.now().strftime("%H:%M:%S")
    nombre = message.from_user.first_name if message.from_user else "Desconocido"
    texto  = message.text or message.caption or "(sin texto)"
    print(f"[{hora}] {nombre}: {texto}")

print("Escuchando mensajes en vivo... (Ctrl+C para salir)")
app.run()
