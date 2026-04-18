import os
import sys
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    """Fuerza que una variable de entorno exista; aborta si falta."""
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
TARGET_USER = os.getenv("TARGET_USER", "@Gabriela51725")

# ── Ruta de sesión (fuera del repo) ───────────────────────────────────────────
# Recomendado: SESSION_PATH=/sdcard/.bot_sessions/
SESSION_PATH = os.path.expanduser(
    os.getenv("SESSION_PATH", "~/telegram-bot-tap")
)

# ── Ruta screenshot temporal ──────────────────────────────────────────────────
SCREENSHOT_PATH = os.getenv("SCREENSHOT_PATH", "/sdcard/Download/tap_screenshot.png")

# ── Horario activo ────────────────────────────────────────────────────────────
START_HOUR = int(os.getenv("START_HOUR", "9"))
END_HOUR   = int(os.getenv("END_HOUR",   "21"))

# ── Tiempos ───────────────────────────────────────────────────────────────────
WAIT_AFTER_OPEN    = int(os.getenv("WAIT_AFTER_OPEN",    "30"))
ERROR_PAUSE_SECONDS = int(os.getenv("ERROR_PAUSE_SECONDS", "60"))
HEARTBEAT_INTERVAL  = int(os.getenv("HEARTBEAT_INTERVAL",  "60"))

# ── Coordenadas de taps ───────────────────────────────────────────────────────
TAP_SEQUENCE = [
    (325.5, 586.5),
    (168.8, 611.5),
]

# ── Modo seguro: velocidad reducida, menos agresivo ───────────────────────────
SAFE_MODE = os.getenv("SAFE_MODE", "false").lower() == "true"

# ── Hosts permitidos para abrir URLs (vacío = sin restricción) ────────────────
_hosts_raw = os.getenv("ALLOWED_URL_HOSTS", "")
ALLOWED_URL_HOSTS: list[str] = [h.strip() for h in _hosts_raw.split(",") if h.strip()]
