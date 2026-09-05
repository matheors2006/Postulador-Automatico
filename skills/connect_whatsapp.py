import base64
import os

import requests

BASE_URL = "http://localhost:8080"
API_KEY = "tu_clave_secreta_aqui"
INSTANCE_NAME = "MiBot"

headers = {"apikey": API_KEY, "Content-Type": "application/json"}

create_response = requests.post(
    f"{BASE_URL}/instance/create",
    headers=headers,
    json={"instanceName": INSTANCE_NAME, "qrcode": True, "integration": "WHATSAPP-BAILEYS"},
)

print("instance/create ->", create_response.status_code)
create_data = create_response.json()
print(create_data)

qr_base64 = create_data["qrcode"]["base64"]
prefix = "data:image/png;base64,"
if qr_base64.startswith(prefix):
    qr_base64 = qr_base64[len(prefix):]

qr_bytes = base64.b64decode(qr_base64)

qr_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "qr_whatsapp.png")
)
with open(qr_path, "wb") as f:
    f.write(qr_bytes)

print(f"QR guardado en: {qr_path}")

webhook_response = requests.post(
    f"{BASE_URL}/webhook/set/{INSTANCE_NAME}",
    headers=headers,
    json={
        "webhook": {
            "enabled": True,
            "url": "http://host.docker.internal:8000/bot/webhook/",
            "byEvents": False,
            "base64": False,
            "events": ["MESSAGES_UPSERT"],
        }
    },
)

print("webhook/set ->", webhook_response.status_code)
print(webhook_response.json())
