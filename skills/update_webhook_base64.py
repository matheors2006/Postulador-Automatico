import requests

BASE_URL = "http://localhost:8080"
API_KEY = "tu_clave_secreta_aqui"
INSTANCE_NAME = "MiBot"

headers = {"apikey": API_KEY, "Content-Type": "application/json"}

response = requests.post(
    f"{BASE_URL}/webhook/set/{INSTANCE_NAME}",
    headers=headers,
    json={
        "webhook": {
            "enabled": True,
            "url": "http://host.docker.internal:8000/bot/webhook/",
            "byEvents": False,
            "base64": True,
            "events": ["MESSAGES_UPSERT"],
        }
    },
)

print("webhook/set ->", response.status_code)
print(response.json())
