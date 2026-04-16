import asyncio
import logging
import os
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message

from config import (
    API_ID, API_HASH, PHONE, GROUP,
    TARGET_USER, START_HOUR, END_HOUR, SCREENSHOT_PATH
)
from parser import parse_message
from adb_controller import connect_device, execute_task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Client("tap_session", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE)

# Lock para evitar que dos tareas corran al mismo tiempo
processing_lock = asyncio.Lock()


def is_active_hours() -> bool:
    now = datetime.now()
    return START_HOUR <= now.hour < END_HOUR


@app.on_message(filters.chat(GROUP) & (filters.text | filters.caption))
async def handle_group_message(client: Client, message: Message):
    if not is_active_hours():
        logger.debug("Fuera de horario, mensaje ignorado.")
        return

    text = message.text or message.caption or ""
    task_number, url = parse_message(text)

    if not url:
        return

    if processing_lock.locked():
        logger.warning("Ya hay una tarea en proceso, mensaje ignorado.")
        return

    async with processing_lock:
        logger.info("Tarea %s detectada. URL: %s", task_number, url)

        # Ejecutar en el celular (corre en thread para no bloquear el loop)
        success = await asyncio.get_event_loop().run_in_executor(
            None, execute_task, url
        )

        if not success:
            logger.error("Fallo la ejecucion en el celular.")
            return

        # Armar caption
        caption = f"Tarea {task_number} completada" if task_number else "Tarea completada"

        # Enviar screenshot a @Gabriela51725
        try:
            await client.send_photo(
                chat_id=TARGET_USER,
                photo=SCREENSHOT_PATH,
                caption=caption
            )
            logger.info("Screenshot enviado a %s: %s", TARGET_USER, caption)
        except Exception as e:
            logger.error("Error enviando screenshot: %s", e)
        finally:
            if os.path.exists(SCREENSHOT_PATH):
                os.remove(SCREENSHOT_PATH)


async def main():
    logger.info("Conectando dispositivo ADB %s...", __import__('config').DEVICE_IP)
    connected = await asyncio.get_event_loop().run_in_executor(None, connect_device)
    if not connected:
        logger.error("No se pudo conectar al dispositivo ADB. Verifica la IP y que el dispositivo tenga ADB por WiFi habilitado.")

    logger.info("Iniciando bot. Activo de %dhs a %dhs.", START_HOUR, END_HOUR)
    await app.start()
    logger.info("Sesion iniciada como %s", (await app.get_me()).username)
    await asyncio.Event().wait()  # Mantener corriendo


if __name__ == "__main__":
    asyncio.run(main())
