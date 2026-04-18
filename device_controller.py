import random
import shlex
import subprocess
import time
import logging
from urllib.parse import urlparse

from config import TAP_SEQUENCE, WAIT_AFTER_OPEN, SCREENSHOT_PATH, SAFE_MODE, ALLOWED_URL_HOSTS

logger = logging.getLogger(__name__)


# ── Helpers internos ──────────────────────────────────────────────────────────

def _root(cmd: str, timeout: int = 30) -> tuple[bool, str]:
    """Ejecuta un comando como root en el dispositivo local."""
    try:
        result = subprocess.run(
            ["su", "-c", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            logger.error("Error root cmd: %s", result.stderr.strip())
            return False, result.stderr.strip()
        return True, result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error("Timeout ejecutando comando root.")
        return False, "timeout"
    except Exception as e:
        logger.error("Excepcion en root cmd: %s", e)
        return False, str(e)


def _human_delay() -> None:
    """Pausa aleatoria para simular comportamiento humano."""
    if SAFE_MODE:
        delay = 5.0 + random.uniform(0, 8)
    else:
        delay = 3.0 + random.uniform(0, 7)
    logger.debug("Pausa: %.1fs", delay)
    time.sleep(delay)


def _validate_url(url: str) -> bool:
    """Valida esquema y, si hay whitelist configurada, el host de la URL."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            logger.warning("Esquema no permitido: %s", parsed.scheme)
            return False
        if ALLOWED_URL_HOSTS and parsed.hostname not in ALLOWED_URL_HOSTS:
            logger.warning("Host bloqueado: %s", parsed.hostname)
            return False
        return True
    except Exception as e:
        logger.error("URL invalida: %s", e)
        return False


# ── Acciones de dispositivo ───────────────────────────────────────────────────

def keep_screen_on() -> None:
    """Mantiene la pantalla encendida indefinidamente (requiere root)."""
    _root("settings put system screen_off_timeout 2147483647")
    _root("echo tap_bot_wakelock > /sys/power/wake_lock")
    logger.info("Pantalla configurada para mantenerse encendida.")


def open_url(url: str) -> bool:
    """Abre una URL en el browser/app del sistema."""
    if not _validate_url(url):
        logger.error("URL rechazada por politica de seguridad.")
        return False
    # shlex.quote previene inyeccion de comandos via la URL
    safe_url = shlex.quote(url)
    ok, _ = _root(f"am start -a android.intent.action.VIEW -d {safe_url}")
    if ok:
        logger.info("URL abierta correctamente.")
    return ok


def tap(x: float, y: float) -> bool:
    """Toca la pantalla en las coordenadas indicadas."""
    ok, _ = _root(f"input tap {int(x)} {int(y)}")
    if ok:
        logger.info("Tap en (%d, %d)", int(x), int(y))
    return ok


def take_screenshot() -> bool:
    """Toma una captura de pantalla y la guarda en SCREENSHOT_PATH."""
    ok, _ = _root(f"screencap -p {shlex.quote(SCREENSHOT_PATH)}")
    if ok:
        logger.info("Screenshot guardado.")
    return ok


def execute_task(url: str) -> bool:
    """
    Pipeline completo:
      1. Abre el link
      2. Espera que cargue (con delay humano)
      3. Toca las coordenadas en orden (con delays entre taps)
      4. Saca screenshot
    Retorna True si todo salio bien.
    """
    if not open_url(url):
        return False

    logger.info("Esperando %ss para que cargue la pagina...", WAIT_AFTER_OPEN)
    time.sleep(WAIT_AFTER_OPEN)

    for i, (x, y) in enumerate(TAP_SEQUENCE, 1):
        logger.info("Tap %d/%d", i, len(TAP_SEQUENCE))
        if not tap(x, y):
            return False
        _human_delay()

    return take_screenshot()
