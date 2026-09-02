from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from bot.tasks import process_job_application


@api_view(["GET", "POST"])
def whatsapp_webhook(request: Request) -> Response:
    """Recibe mensajes entrantes de WhatsApp y encola postulaciones."""
    if request.method == "GET":
        return Response({"status": "ok", "message": "Webhook escuchando"})

    text: str = request.data.get("text", "")

    job_url = next(
        (token for token in text.split() if "http" in token),
        None,
    )

    if job_url:
        process_job_application.delay(job_url, "Texto CV temporal", "skills/dummy_cv.pdf")

    return Response({"status": "queued"})
