import os

import requests

WEBHOOK_URL = "http://127.0.0.1:8000/bot/webhook/"
PHONE = "123456789"

dummy_cv_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "dummy_cv.pdf")
)

with open(dummy_cv_path, "rb") as cv_file:
    response_cv = requests.post(
        WEBHOOK_URL,
        data={"phone": PHONE},
        files={"cv_file": cv_file},
    )

print("Respuesta subida de CV:")
print(response_cv.status_code, response_cv.json())

response_link = requests.post(
    WEBHOOK_URL,
    json={"phone": PHONE, "body": "Link: https://ejemplo.com"},
)

print("Respuesta envio de link:")
print(response_link.status_code, response_link.json())
