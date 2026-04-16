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
from device_controller import execute_task, keep_screen_on

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.expanduser("~/telegram-bot-tap/bot.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Client(
    "tap_session",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE,
    workdir=os.path.expanduser("~/telegram-bot-tap")
)

# Evita que dos tareas corran al mismo tiempo
processing_lock = asyncio.Lock()


def is_active_hours() -> bool:
    now = datetime.now()
    return START_HOUR <= now.hour < END_HOUR


@app.on_message(filters.chat(GROUP) & (filters.text | filters.caption))
async def handle_group_message(client: Client, message: Message):
    if not is_active_hours():
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

        success = await asyncio.get_event_loop().run_in_executor(
            None, execute_task, url
        )

        if not success:
            logger.error("Fallo la ejecucion en pantalla.")
            return

        caption = f"Tarea {task_number} completada" if task_number else "Tarea completada"

        try:
            await client.send_photo(
                chat_id=TARGET_USER,
                photo=SCREENSHOT_PATH,
                caption=caption
            )
            logger.info("Enviado a %s: %s", TARGET_USER, caption)
        except Exception as e:
            logger.error("Error al enviar screenshot: %s", e)
        finally:
            if os.path.exists(SCREENSHOT_PATH):
                os.remove(SCREENSHOT_PATH)


async def main():
    logger.info("Iniciando bot. Activo de %dhs a %dhs.", START_HOUR, END_HOUR)

    # Mantener pantalla encendida
    await asyncio.get_event_loop().run_in_executor(None, keep_screen_on)

    await app.start()
    me = await app.get_me()
    nombre = me.username or me.first_name or me.phone_number
    logger.info("Sesion iniciada como %s", nombre)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
