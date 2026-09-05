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

SYSTEM_PROMPT_TEMPLATE = (
    "Eres el candidato que postula a un empleo. Debes responder los campos "
    "de un formulario de postulacion (Easy Apply) basandote en el CV proporcionado "
    "(delimitado como CV_TEXT), pero SIEMPRE debes exagerar y elevar el perfil "
    "para maximizar las posibilidades de contratacion. "
    "REGLA 1 (Tecnologias nuevas): Si el formulario pregunta por una tecnologia, "
    "lenguaje o herramienta que NO esta en el CV, ASUME QUE SI LA SABES. "
    "Inventa aleatoriamente entre 3 y 4 anios de experiencia para esa tecnologia. "
    "REGLA 2 (Banca): Si el formulario pregunta por experiencia en el 'Sector Banca', "
    "'Bancario', o 'Financiero', DEBES responder categoricamente que NO tienes "
    "experiencia (0 anios o 'No'). Esta es la unica excepcion donde no debes alucinar. "
    "REGLA 3 (Instrucciones extra): Toma en cuenta estas INSTRUCCIONES EXTRA del "
    "usuario: {extra_instructions}. Si el usuario define un rango salarial aqui, usalo. "
    "Si el formulario no permite letras en campos de salario, extrae solo el numero "
    "logico de ese rango. "
    "Debes devolver EXCLUSIVAMENTE un objeto JSON plano donde cada llave es el "
    "'id' del campo recibido en FORM_FIELDS y el valor es la respuesta decidida "
    "para ese campo (string, numero o la opcion elegida). No incluyas explicaciones "
    "ni texto adicional."
    
)


class JobApplicationBrain:
    """Decide las respuestas de un formulario de postulacion usando un LLM."""

    @staticmethod
    def solve_form(
        cv_text: str, form_fields: list[dict[str, Any]], extra_instructions: str = ""
    ) -> dict[str, Any]:
        """
        Resuelve los valores a introducir en un formulario de postulacion.

        Args:
            cv_text: Texto plano extraido del CV del candidato.
            form_fields: Lista de campos extraidos por Playwright, cada uno
                como un diccionario (ej. {"id": "q1", "type": "text",
                "label": "Anios de experiencia"}).
            extra_instructions: Preferencias adicionales del candidato
                capturadas por chat (rango salarial, disponibilidad, etc.).

        Returns:
            Un diccionario cuyas llaves son los "id" de form_fields y cuyos
            valores son la respuesta decidida por el LLM para cada campo.
        """
        client = OpenAI(base_url=GROQ_BASE_URL, api_key=os.getenv("GROQ_API_KEY"))

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            extra_instructions=extra_instructions or "Ninguna."
        )

        user_prompt = (
            f"CV_TEXT:\n{cv_text}\n\n"
            f"FORM_FIELDS:\n{json.dumps(form_fields, ensure_ascii=False)}"
        )

        response = client.chat.completions.create(
            model=GROQ_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        content = response.choices[0].message.content
        return json.loads(content)
