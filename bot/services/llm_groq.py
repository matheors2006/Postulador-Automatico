"""
Motor de razonamiento para completar formularios de postulación (Easy Apply).

Usa el modelo `openai/gpt-oss-120b` alojado en Groq (vía cliente oficial de
`openai` apuntando a la API compatible de Groq) para decidir, a partir del
texto de un CV, qué valor colocar en cada campo de un formulario extraído
por Playwright.
"""

import json
import os
from typing import Any

from openai import OpenAI

GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

SYSTEM_PROMPT = (
    "Eres el candidato que postula a un empleo. Debes responder los campos "
    "de un formulario de postulacion (Easy Apply) exactamente como lo haria "
    "esa persona, basando CADA respuesta UNICAMENTE en la informacion "
    "presente en su CV (delimitado como CV_TEXT). No inventes datos, "
    "titulos, anios de experiencia, ni habilidades que no esten explicita o "
    "razonablemente implicitas en el CV. Si el CV no contiene informacion "
    "suficiente para responder un campo con certeza, entrega la respuesta "
    "mas conservadora y honesta posible (por ejemplo 'No especificado' o "
    "un valor negativo/cero segun corresponda al tipo de campo). "
    "Debes devolver EXCLUSIVAMENTE un objeto JSON plano donde cada llave es "
    "el 'id' del campo recibido en FORM_FIELDS y el valor es la respuesta "
    "decidida para ese campo (string, numero o la opcion elegida). No "
    "incluyas explicaciones, texto adicional ni claves que no esten en "
    "FORM_FIELDS."
)


class JobApplicationBrain:
    """Decide las respuestas de un formulario de postulacion usando un LLM."""

    @staticmethod
    def solve_form(cv_text: str, form_fields: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Resuelve los valores a introducir en un formulario de postulacion.

        Args:
            cv_text: Texto plano extraido del CV del candidato.
            form_fields: Lista de campos extraidos por Playwright, cada uno
                como un diccionario (ej. {"id": "q1", "type": "text",
                "label": "Anios de experiencia"}).

        Returns:
            Un diccionario cuyas llaves son los "id" de form_fields y cuyos
            valores son la respuesta decidida por el LLM para cada campo.
        """
        client = OpenAI(base_url=GROQ_BASE_URL, api_key=os.getenv("GROQ_API_KEY"))

        user_prompt = (
            f"CV_TEXT:\n{cv_text}\n\n"
            f"FORM_FIELDS:\n{json.dumps(form_fields, ensure_ascii=False)}"
        )

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content
        return json.loads(content)
