import os
from dotenv import load_dotenv

load_dotenv()

# Credenciales Telegram
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")

# Grupo a monitorear
GROUP = os.getenv("GROUP")

# Usuario destino de los reportes
TARGET_USER = "@Gabriela51725"

# ADB - celular Android
DEVICE_IP = os.getenv("DEVICE_IP")
DEVICE_PORT = int(os.getenv("DEVICE_PORT", "5555"))

# Coordenadas donde tocar (en orden)
TAP_SEQUENCE = [
    (325.5, 586.5),
    (168.8, 611.5),
]

# Horario activo (hora local del sistema)
START_HOUR = 9   # 9am
END_HOUR = 21    # 9pm

# Segundos de espera tras abrir el link antes de tocar
WAIT_AFTER_OPEN = 4

# Archivo temporal de screenshot
SCREENSHOT_PATH = "/tmp/tap_screenshot.png"
