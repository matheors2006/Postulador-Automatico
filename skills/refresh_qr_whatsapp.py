import base64
import os

import requests

BASE_URL = "http://localhost:8080"
API_KEY = "tu_clave_secreta_aqui"
INSTANCE_NAME = "MiBot"

headers = {"apikey": API_KEY}

connect_response = requests.get(
    f"{BASE_URL}/instance/connect/{INSTANCE_NAME}",
    headers=headers,
)

print("instance/connect ->", connect_response.status_code)
connect_data = connect_response.json()
print(connect_data)

qr_base64 = connect_data.get("base64") or connect_data.get("qrcode", {}).get("base64")

prefix = "data:image/png;base64,"
if qr_base64.startswith(prefix):
    qr_base64 = qr_base64[len(prefix):]

qr_bytes = base64.b64decode(qr_base64)

qr_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "qr_whatsapp.png")
)
with open(qr_path, "wb") as f:
    f.write(qr_bytes)

print(f"QR sobrescrito en: {qr_path}")
