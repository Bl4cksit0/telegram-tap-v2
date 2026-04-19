import os
import sys
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    val = os.getenv(name, "").strip()
    if not val:
        print(f"[ERROR] Variable de entorno requerida no definida: {name}")
        sys.exit(1)
    return val


# ── Credenciales Telegram ─────────────────────────────────────────────────────
API_ID   = int(_require("API_ID"))
API_HASH = _require("API_HASH")
PHONE    = _require("PHONE")

# ── Grupo y destino ───────────────────────────────────────────────────────────
GROUP       = _require("GROUP")
TARGET_USER = os.getenv("TARGET_USER", "@ThorBcKBot")

# ── Ruta de sesión ────────────────────────────────────────────────────────────
SESSION_PATH = os.path.expanduser(
    os.getenv("SESSION_PATH", "~/telegram-bot-tap")
)

# ── Horario activo ────────────────────────────────────────────────────────────
START_HOUR = int(os.getenv("START_HOUR", "9"))
END_HOUR   = int(os.getenv("END_HOUR",   "21"))

# ── Tiempos ───────────────────────────────────────────────────────────────────
ERROR_PAUSE_SECONDS = int(os.getenv("ERROR_PAUSE_SECONDS", "60"))
HEARTBEAT_INTERVAL  = int(os.getenv("HEARTBEAT_INTERVAL",  "60"))
