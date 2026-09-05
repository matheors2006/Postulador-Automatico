import json

import requests

BASE_URL = "http://localhost:8080"
API_KEY = "tu_clave_secreta_aqui"
INSTANCE_NAME = "MiBot"

headers = {"apikey": API_KEY, "Content-Type": "application/json"}

response = requests.post(
    f"{BASE_URL}/message/sendText/{INSTANCE_NAME}",
    headers=headers,
    json={
        "number": "51922852750",
        "text": (
            "¡Hola Matheo! Soy tu Postulador Automático 🤖. Los motores están "
            "encendidos y mi conexión a WhatsApp funciona. Por favor, mándame "
            "tu CV en PDF por este chat para guardarlo en mi memoria."
        ),
    },
)

print("message/sendText ->", response.status_code)
print(json.dumps(response.json(), ensure_ascii=True))
