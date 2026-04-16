import os
from dotenv import load_dotenv

load_dotenv()

# Credenciales Telegram - obtener en https://my.telegram.org
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")

# Grupo de Telegram a monitorear (username sin @ o ID numerico)
GROUP = os.getenv("GROUP")

# Usuario destino de los reportes
TARGET_USER = "@Gabriela51725"

# Coordenadas donde tocar en orden
TAP_SEQUENCE = [
    (325.5, 586.5),
    (168.8, 611.5),
]

# Horario activo
START_HOUR = 9   # 9am
END_HOUR = 21    # 9pm

# Segundos de espera tras abrir el link antes de tocar
WAIT_AFTER_OPEN = 4

# Ruta del screenshot temporal (en almacenamiento interno)
SCREENSHOT_PATH = "/sdcard/Download/tap_screenshot.png"
