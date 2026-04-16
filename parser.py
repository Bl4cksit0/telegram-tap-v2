import re

# Mapa de emojis numericos a digitos
EMOJI_DIGIT_MAP = {
    '\u0030\ufe0f\u20e3': '0', '\u0031\ufe0f\u20e3': '1',
    '\u0032\ufe0f\u20e3': '2', '\u0033\ufe0f\u20e3': '3',
    '\u0034\ufe0f\u20e3': '4', '\u0035\ufe0f\u20e3': '5',
    '\u0036\ufe0f\u20e3': '6', '\u0037\ufe0f\u20e3': '7',
    '\u0038\ufe0f\u20e3': '8', '\u0039\ufe0f\u20e3': '9',
    # Sin variation selector
    '\u0030\u20e3': '0', '\u0031\u20e3': '1',
    '\u0032\u20e3': '2', '\u0033\u20e3': '3',
    '\u0034\u20e3': '4', '\u0035\u20e3': '5',
    '\u0036\u20e3': '6', '\u0037\u20e3': '7',
    '\u0038\u20e3': '8', '\u0039\u20e3': '9',
}


def _decode_emoji_numbers(text: str) -> str:
    for emoji, digit in EMOJI_DIGIT_MAP.items():
        text = text.replace(emoji, digit)
    return text


def extract_task_number(text: str) -> str | None:
    decoded = _decode_emoji_numbers(text)
    # Buscar secuencia de digitos que venga de emojis numericos
    # En el mensaje original los emojis estan en la primera linea
    first_line = decoded.splitlines()[0] if decoded else ""
    numbers = re.findall(r'\d+', first_line)
    for n in numbers:
        if n.isdigit():
            return n
    return None


def extract_url(text: str) -> str | None:
    urls = re.findall(r'https?://\S+', text)
    return urls[0].rstrip('.,)') if urls else None


def parse_message(text: str) -> tuple[str | None, str | None]:
    """
    Retorna (task_number, url) si el mensaje tiene el formato esperado,
    o (None, None) si no aplica.
    Formato esperado:
        🔠🔠🔠🔠🔠    2️⃣7️⃣
        1. Instruccion...
        https://...
    """
    if not text:
        return None, None

    url = extract_url(text)
    if not url:
        return None, None

    task_number = extract_task_number(text)
    return task_number, url
