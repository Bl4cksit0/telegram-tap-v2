import asyncio
import logging
import os
import re
import shlex
import subprocess
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message

from config import (
    API_ID, API_HASH, PHONE, GROUP,
    TARGET_USER, START_HOUR, END_HOUR,
    SESSION_PATH, ERROR_PAUSE_SECONDS, HEARTBEAT_INTERVAL,
)
from parser import parse_message


class _SanitizeFilter(logging.Filter):
    _PATTERNS = [
        (re.compile(r'(api_hash[=:\s])\S+',   re.I), r'\1***'),
        (re.compile(r'(api_id[=:\s])\S+',     re.I), r'\1***'),
        (re.compile(r'(session[=:\s])\S+',    re.I), r'\1***'),
        (re.compile(r'(hash[=:\s])[0-9a-f]+', re.I), r'\1***'),
        (re.compile(r'\+\d{8,15}'),            '+***'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        for pattern, replacement in self._PATTERNS:
            msg = pattern.sub(replacement, msg)
        record.msg  = msg
        record.args = ()
        return True


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

app = Client(
    "tap_session",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE,
    workdir=SESSION_PATH,
)

processing_lock = asyncio.Lock()


def is_active_hours() -> bool:
    return START_HOUR <= datetime.now().hour < END_HOUR


def open_in_telegram_app(url: str) -> bool:
    """Abre la URL en la app de Telegram instalada en el celular."""
    safe_url = shlex.quote(url)
    try:
        result = subprocess.run(
            ["su", "-c", f"am start -a android.intent.action.VIEW -d {safe_url} -p org.telegram.messenger"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            logger.info("URL abierta en Telegram app.")
            return True
        logger.error("Error al abrir URL: %s", result.stderr.strip())
        return False
    except Exception as e:
        logger.error("Excepcion abriendo URL: %s", e)
        return False


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
        logger.info("Tarea %s detectada: %s", task_number, url)

        await asyncio.get_event_loop().run_in_executor(None, open_in_telegram_app, url)

        caption = f"Tarea {task_number}\n{url}" if task_number else url

        try:
            await client.send_message(chat_id=TARGET_USER, text=caption)
            logger.info("Link enviado a %s", TARGET_USER)
        except Exception as e:
            logger.error("Error al enviar mensaje: %s", e)
            await asyncio.sleep(ERROR_PAUSE_SECONDS)


async def _heartbeat():
    while True:
        logger.info("heartbeat OK")
        await asyncio.sleep(HEARTBEAT_INTERVAL)


async def _run():
    logger.info("Iniciando bot. Activo de %dhs a %dhs.", START_HOUR, END_HOUR)
    await app.start()
    me = await app.get_me()
    logger.info("Sesion iniciada como %s", me.username or me.first_name)
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
