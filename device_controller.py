import subprocess
import time
import logging
from config import TAP_SEQUENCE, WAIT_AFTER_OPEN, SCREENSHOT_PATH

logger = logging.getLogger(__name__)


def _root(cmd: str, timeout: int = 30) -> tuple[bool, str]:
    """Ejecuta un comando como root en el dispositivo local."""
    try:
        result = subprocess.run(
            ["su", "-c", cmd],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            logger.error("Error root cmd '%s': %s", cmd, result.stderr.strip())
            return False, result.stderr.strip()
        return True, result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error("Timeout ejecutando: %s", cmd)
        return False, "timeout"
    except Exception as e:
        logger.error("Excepcion en root cmd: %s", e)
        return False, str(e)


def open_url(url: str) -> bool:
    """Abre una URL en el browser/app del sistema."""
    ok, out = _root(f'am start -a android.intent.action.VIEW -d "{url}"')
    if ok:
        logger.info("URL abierta: %s", url)
    return ok


def tap(x: float, y: float) -> bool:
    """Toca la pantalla en las coordenadas indicadas."""
    ok, _ = _root(f"input tap {int(x)} {int(y)}")
    if ok:
        logger.info("Tap en (%s, %s)", int(x), int(y))
    return ok


def take_screenshot() -> bool:
    """Toma una captura de pantalla y la guarda en SCREENSHOT_PATH."""
    ok, _ = _root(f"screencap -p {SCREENSHOT_PATH}")
    if ok:
        logger.info("Screenshot guardado en %s", SCREENSHOT_PATH)
    return ok


def execute_task(url: str) -> bool:
    """
    Pipeline completo:
      1. Abre el link
      2. Espera que cargue
      3. Toca las coordenadas en orden
      4. Saca screenshot
    Retorna True si todo salio bien.
    """
    if not open_url(url):
        return False

    logger.info("Esperando %ss para que cargue la pagina...", WAIT_AFTER_OPEN)
    time.sleep(WAIT_AFTER_OPEN)

    for i, (x, y) in enumerate(TAP_SEQUENCE, 1):
        logger.info("Tap %d/%d en (%s, %s)", i, len(TAP_SEQUENCE), x, y)
        if not tap(x, y):
            return False
        time.sleep(1)

    return take_screenshot()
