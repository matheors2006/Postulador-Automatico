import base64
import time
from datetime import datetime

import requests

BASE_URL = "http://localhost:8080"
API_KEY = "tu_clave_secreta_aqui"
INSTANCE_NAME = "MiBot"
REFRESH_SECONDS = 15

headers = {"apikey": API_KEY}

while True:
    try:
        response = requests.get(
            f"{BASE_URL}/instance/connect/{INSTANCE_NAME}",
            headers=headers,
        )
        data = response.json()

        qr_base64 = data.get("base64") or data.get("qrcode", {}).get("base64")

        prefix = "data:image/png;base64,"
        if qr_base64.startswith(prefix):
            qr_base64 = qr_base64[len(prefix):]

        qr_bytes = base64.b64decode(qr_base64)

        with open("qr_whatsapp.png", "wb") as f:
            f.write(qr_bytes)

        now = datetime.now().strftime("%H:%M:%S")
        print(
            f"[OK] QR actualizado a las {now}. Abre qr_whatsapp.png en VS Code. "
            f"El próximo refresco será en {REFRESH_SECONDS} segundos..."
        )
    except requests.exceptions.RequestException as exc:
        print(f"[WARN] Fallo de red al pedir el QR: {exc}")

    time.sleep(REFRESH_SECONDS)
