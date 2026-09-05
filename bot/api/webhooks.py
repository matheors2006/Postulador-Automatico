import base64
import re
from typing import Any, Optional

from django.core.files.base import ContentFile
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from bot.models import CandidateProfile
from bot.tasks import process_job_application

DEFAULT_PHONE_NUMBER = "51999999999"
ALLOWED_NUMBER = "51922852750"
URL_PATTERN = re.compile(r"(https?://[^\s]+)")


def _find_base64(data: dict[str, Any]) -> Optional[str]:
    """Busca recursivamente una llave 'base64' dentro de un diccionario anidado."""
    base64_value = data.get("base64")
    if isinstance(base64_value, str):
        return base64_value

    for value in data.values():
        if isinstance(value, dict):
            found = _find_base64(value)
            if found:
                return found

    return None


def _extract_text(message: dict[str, Any]) -> str:
    """Extrae el texto de un mensaje de Evolution (texto simple o extendido)."""
    conversation = message.get("conversation")
    if isinstance(conversation, str):
        return conversation

    extended = message.get("extendedTextMessage")
    if isinstance(extended, dict):
        return extended.get("text", "")

    return ""


@api_view(["GET", "POST"])
def whatsapp_webhook(request: Request) -> Response:
    """Recibe eventos de Evolution API: subida de CV (base64) o link a postular."""
    if request.method == "GET":
        return Response({"status": "ok", "message": "Webhook escuchando"})

    if request.data.get("event") != "messages.upsert":
        return Response({"status": "ignored", "message": "Evento no manejado"})

    data: dict[str, Any] = request.data.get("data", {})

    remote_jid: str = data.get("key", {}).get("remoteJid", "")
    phone_number = remote_jid.split("@")[0] or DEFAULT_PHONE_NUMBER

    if phone_number != ALLOWED_NUMBER or "@g.us" in remote_jid:
        return Response({"status": "ignored", "message": "Chat no autorizado"})

    message: dict[str, Any] = data.get("message", {})
    text = _extract_text(message)

    cv_base64 = _find_base64(data)

    if cv_base64:
        profile, _ = CandidateProfile.objects.get_or_create(phone_number=phone_number)
        cv_bytes = base64.b64decode(cv_base64)
        profile.cv_file.save("cv.pdf", ContentFile(cv_bytes), save=True)
        return Response({"status": "cv_saved", "message": "CV guardado"})

    if "http" in text:
        url_match = URL_PATTERN.search(text)
        job_url = url_match.group(1) if url_match else text

        try:
            profile = CandidateProfile.objects.get(phone_number=phone_number)
        except CandidateProfile.DoesNotExist:
            profile = None

        if not profile or not profile.cv_file:
            return Response(
                {"status": "error", "message": "Primero debes enviar tu CV en formato PDF"}
            )

        process_job_application.delay(job_url, profile.cv_file.path)
        return Response({"status": "queued"})

    if text:
        profile, _ = CandidateProfile.objects.get_or_create(phone_number=phone_number)
        profile.extra_instructions += f"\n- {text}"
        profile.save()
        return Response(
            {"status": "instruction_saved", "message": "Instrucción guardada en memoria"}
        )

    return Response({"status": "ignored", "message": "Mensaje no reconocido"})
