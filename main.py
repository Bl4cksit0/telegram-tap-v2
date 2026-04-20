import asyncio
import logging
import os
import re

from pyrogram import Client, filters
from pyrogram.types import Message

from config import (
    API_ID, API_HASH, PHONE, GROUP,
    SESSION_PATH, ERROR_PAUSE_SECONDS, HEARTBEAT_INTERVAL,
)


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


async def _load_history(client: Client):
    print("\n" + "="*60)
    print(f"  HISTORIAL DEL GRUPO: {GROUP}")
    print("="*60)
    messages = []
    async for msg in client.get_chat_history(GROUP, limit=50):
        messages.append(msg)

    if not messages:
        print("  (sin mensajes previos)")
    else:
        for msg in reversed(messages):
            text   = msg.text or msg.caption or "[sin texto]"
            sender = msg.from_user.first_name if msg.from_user else "Desconocido"
            ts     = msg.date.strftime("%Y-%m-%d %H:%M:%S")
            print(f"  [{ts}] {sender}: {text}")

    print("="*60)
    print(f"  {len(messages)} mensajes cargados. Escuchando en vivo...\n")


@app.on_message(filters.chat(GROUP) & (filters.text | filters.caption))
async def show_live_message(client: Client, message: Message):
    text   = message.text or message.caption or "[sin texto]"
    sender = message.from_user.first_name if message.from_user else "Desconocido"
    ts     = message.date.strftime("%H:%M:%S")
    print(f"[LIVE {ts}] {sender}: {text}")


async def _heartbeat():
    while True:
        logger.info("heartbeat OK")
        await asyncio.sleep(HEARTBEAT_INTERVAL)


async def _run():
    logger.info("Iniciando bot.")
    await app.start()
    me = await app.get_me()
    logger.info("Sesion iniciada como %s", me.username or me.first_name)
    await _load_history(app)
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
