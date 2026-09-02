# Proyecto: Auto-Jobs Bot

## Arquitectura Base

- Django REST Framework para webhooks de WhatsApp.
- Celery + Redis para encolar la navegación (Playwright) y no bloquear peticiones HTTP.
- Servicios Modulares: Cero lógica de negocio en las vistas/endpoints. Todo se inyecta desde `bot/services/`.
- LLM: Groq (Llama-3.3-70B) mediante el cliente oficial de `openai` en Python.

## Reglas de Código (Python)

- Usa tipado estricto (Type Hinting) en TODAS las funciones y métodos.
- Retorna JSON estructurado (Pydantic o diccionarios tipados) desde los servicios.
- Manejo de excepciones explícito: Nunca uses `except Exception: pass`. Intercepta errores de Playwright (`playwright.core.Error`) y APIs por separado.

## Optimización de Contexto (Reglas para Claude Code)

- NUNCA leas un archivo completo si solo necesitas modificar una función. Usa comandos grep o herramientas de búsqueda de texto para encontrar la línea exacta.
- Antes de modificar lógica compleja de Playwright o el LLM, utiliza los scripts de la carpeta `skills/` para probar la función de forma aislada.
- No des explicaciones largas de los cambios; solo ejecuta los comandos y modifica los archivos.
