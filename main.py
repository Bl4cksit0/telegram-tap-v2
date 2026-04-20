import asyncio
import glob
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


_log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot.log")
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


# ── Sesión ────────────────────────────────────────────────────────────────────
def _delete_session() -> None:
    for path in glob.glob(os.path.join(SESSION_PATH, "tap_session.session*")):
        try:
            os.remove(path)
            logger.info("Sesion borrada: %s", path)
        except OSError as e:
            logger.warning("No se pudo borrar sesion %s: %s", path, e)


app = Client(
    "tap_session",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE,
    workdir=SESSION_PATH,
)


# ── Mensajes en vivo ──────────────────────────────────────────────────────────
@app.on_message(filters.chat(GROUP) & (filters.text | filters.caption))
async def show_live_message(client: Client, message: Message):
    text   = message.text or message.caption or "[sin texto]"
    sender = message.from_user.first_name if message.from_user else "Desconocido"
    ts     = message.date.strftime("%H:%M:%S")
    print(f"[LIVE {ts}] {sender}: {text}")


# ── Comando logout (mensajes guardados) ───────────────────────────────────────
@app.on_message(filters.private & filters.me & filters.text)
async def handle_self_command(client: Client, message: Message):
    if message.text.strip().lower() == "logout":
        logger.info("Comando logout recibido. Borrando sesion y apagando.")
        await app.stop()
        _delete_session()
        os._exit(0)


# ── Heartbeat ─────────────────────────────────────────────────────────────────
async def _heartbeat():
    while True:
        logger.info("heartbeat OK")
        await asyncio.sleep(HEARTBEAT_INTERVAL)


# ── Main ──────────────────────────────────────────────────────────────────────
async def _run():
    logger.info("Iniciando bot. Borrando sesion anterior para nueva verificacion...")
    _delete_session()

    logger.info("Ingresa el codigo de verificacion de Telegram cuando se solicite.")
    await app.start()
    me = await app.get_me()
    logger.info("Sesion iniciada como %s. Escuchando mensajes en vivo.", me.username or me.first_name)
    logger.info("Para cerrar sesion y apagar: envia 'logout' a tus Mensajes guardados.")

    asyncio.create_task(_heartbeat())
    await asyncio.Event().wait()


async def main():
    while True:
        try:
            await _run()
        except SystemExit:
            raise
        except Exception as e:
            logger.error("Error fatal: %s. Reiniciando en %ds...", e, ERROR_PAUSE_SECONDS)
            await asyncio.sleep(ERROR_PAUSE_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
