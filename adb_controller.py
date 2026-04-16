import subprocess
import time
import logging
from config import DEVICE_IP, DEVICE_PORT, TAP_SEQUENCE, WAIT_AFTER_OPEN, SCREENSHOT_PATH

logger = logging.getLogger(__name__)


def _adb(args: list[str], timeout: int = 30) -> tuple[bool, str]:
    target = f"{DEVICE_IP}:{DEVICE_PORT}"
    cmd = ["adb", "-s", target] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            logger.error("ADB error: %s", result.stderr.strip())
            return False, result.stderr.strip()
        return True, result.stdout.strip()
    except subprocess.TimeoutExpired:
        logger.error("ADB command timed out: %s", args)
        return False, "timeout"
    except FileNotFoundError:
        logger.error("adb no encontrado. Instala Android Platform Tools.")
        return False, "adb not found"


def connect_device() -> bool:
    result = subprocess.run(
        ["adb", "connect", f"{DEVICE_IP}:{DEVICE_PORT}"],
        capture_output=True, text=True, timeout=15
    )
    output = result.stdout.strip()
    logger.info("ADB connect: %s", output)
    return "connected" in output or "already connected" in output


def open_url(url: str) -> bool:
    ok, _ = _adb([
        "shell", "am", "start",
        "-a", "android.intent.action.VIEW",
        "-d", url
    ])
    return ok


def tap(x: float, y: float) -> bool:
    ok, _ = _adb(["shell", "input", "tap", str(int(x)), str(int(y))])
    return ok


def take_screenshot() -> bool:
    target = f"{DEVICE_IP}:{DEVICE_PORT}"
    try:
        with open(SCREENSHOT_PATH, "wb") as f:
            result = subprocess.run(
                ["adb", "-s", target, "exec-out", "screencap", "-p"],
                stdout=f, stderr=subprocess.PIPE, timeout=30
            )
        return result.returncode == 0
    except Exception as e:
        logger.error("Screenshot error: %s", e)
        return False


def execute_task(url: str) -> bool:
    """
    Abre el link, espera, toca las coordenadas definidas y saca screenshot.
    Retorna True si todo salio bien.
    """
    logger.info("Abriendo URL: %s", url)
    if not open_url(url):
        return False

    logger.info("Esperando %s segundos para que cargue...", WAIT_AFTER_OPEN)
    time.sleep(WAIT_AFTER_OPEN)

    for i, (x, y) in enumerate(TAP_SEQUENCE, 1):
        logger.info("Tap %d en (%s, %s)", i, x, y)
        if not tap(x, y):
            return False
        time.sleep(1)

    logger.info("Tomando screenshot...")
    return take_screenshot()
