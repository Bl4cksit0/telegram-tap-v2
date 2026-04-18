import asyncio
import logging
import os
import re
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message

from config import (
    API_ID, API_HASH, PHONE, GROUP,
    TARGET_USER, START_HOUR, END_HOUR,
    SCREENSHOT_PATH, SESSION_PATH,
    ERROR_PAUSE_SECONDS, HEARTBEAT_INTERVAL,
    SAFE_MODE,
)
from parser import parse_message
from device_controller import execute_task, keep_screen_on


# ── Filtro de sanitización para logs ─────────────────────────────────────────
class _SanitizeFilter(logging.Filter):
    _PATTERNS = [
        (re.compile(r'(api_hash[=:\s])\S+',  re.I), r'\1***'),
        (re.compile(r'(api_id[=:\s])\S+',    re.I), r'\1***'),
        (re.compile(r'(session[=:\s])\S+',   re.I), r'\1***'),
        (re.compile(r'(hash[=:\s])[0-9a-f]+', re.I), r'\1***'),
        (re.compile(r'\+\d{8,15}'),           '+***'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern, replacement in self._PATTERNS:
            msg = pattern.sub(replacement, msg)
        record.msg  = msg
        record.args = ()
        return True


# ── Configuración de logging ──────────────────────────────────────────────────
_log_path = os.path.join(os.path.expanduser("~/telegram-bot-tap"), "bot.log")
_handler_file   = logging.FileHandler(_log_path)
_handler_stream = logging.StreamHandler()
_sanitizer      = _SanitizeFilter()

for _h in (_handler_file, _handler_stream):
    _h.addFilter(_sanitizer)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[_handler_file, _handler_stream],
)
logger = logging.getLogger(__name__)

if SAFE_MODE:
    logger.info("SAFE_MODE activo: velocidad reducida.")

# ── Cliente Pyrogram ──────────────────────────────────────────────────────────
app = Client(
    "tap_session",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE,
    workdir=SESSION_PATH,       # sesión guardada fuera del repo
)

processing_lock = asyncio.Lock()


def is_active_hours() -> bool:
    return START_HOUR <= datetime.now().hour < END_HOUR


# ── Handler de mensajes ───────────────────────────────────────────────────────
@app.on_message(filters.chat(GROUP) & (filters.text | filters.caption))
async def handle_group_message(client: Client, message: Message):
    if not is_active_hours():
        return

    text = message.text or message.caption or ""
    task_number, url = parse_message(text)

    if not url:
        return

    if processing_lock.locked():
        logger.warning("Tarea en proceso, mensaje ignorado.")
        return

    async with processing_lock:
        logger.info("Tarea %s detectada.", task_number)

        try:
            success = await asyncio.get_event_loop().run_in_executor(
                None, execute_task, url
            )
        except Exception as e:
            logger.error("Error ejecutando tarea: %s. Pausando %ds.", e, ERROR_PAUSE_SECONDS)
            await asyncio.sleep(ERROR_PAUSE_SECONDS)
            return

        if not success:
            logger.error("Fallo la ejecucion en pantalla. Pausando %ds.", ERROR_PAUSE_SECONDS)
            await asyncio.sleep(ERROR_PAUSE_SECONDS)
            return

        caption = f"Tarea {task_number} completada" if task_number else "Tarea completada"

        try:
            await client.send_photo(
                chat_id=TARGET_USER,
                photo=SCREENSHOT_PATH,
                caption=caption,
            )
            logger.info("Enviado a %s: %s", TARGET_USER, caption)
        except Exception as e:
            logger.error("Error al enviar screenshot: %s", e)
        finally:
            if os.path.exists(SCREENSHOT_PATH):
                os.remove(SCREENSHOT_PATH)


# ── Heartbeat (watchdog interno) ──────────────────────────────────────────────
async def _heartbeat():
    while True:
        logger.info("heartbeat OK")
        await asyncio.sleep(HEARTBEAT_INTERVAL)


# ── Main ──────────────────────────────────────────────────────────────────────
async def _run():
    logger.info("Iniciando bot. Activo de %dhs a %dhs.", START_HOUR, END_HOUR)
    await asyncio.get_event_loop().run_in_executor(None, keep_screen_on)

    await app.start()
    me = await app.get_me()
    nombre = me.username or me.first_name or "desconocido"
    logger.info("Sesion iniciada como %s", nombre)

    asyncio.create_task(_heartbeat())
    await asyncio.Event().wait()


async def main():
    while True:
        try:
            await _run()
        except Exception as e:
            logger.error("Error fatal: %s. Reiniciando en %ds...", e, ERROR_PAUSE_SECONDS)
            await asyncio.sleep(ERROR_PAUSE_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
