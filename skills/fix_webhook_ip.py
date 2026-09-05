import socket

import requests

BASE_URL = "http://localhost:8080"
API_KEY = "tu_clave_secreta_aqui"
INSTANCE_NAME = "MiBot"

local_ip = socket.gethostbyname(socket.gethostname())
print(f"IP local detectada: {local_ip}")

webhook_url = f"http://{local_ip}:8000/bot/webhook/"

headers = {"apikey": API_KEY, "Content-Type": "application/json"}

response = requests.post(
    f"{BASE_URL}/webhook/set/{INSTANCE_NAME}",
    headers=headers,
    json={
        "webhook": {
            "enabled": True,
            "url": webhook_url,
            "byEvents": False,
            "base64": True,
            "events": ["MESSAGES_UPSERT"],
        }
    },
)

print("webhook/set ->", response.status_code)
print(response.json())
