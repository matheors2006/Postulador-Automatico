from celery import shared_task
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from bot.services.browser_engine import FormAutomation
from bot.services.llm_groq import JobApplicationBrain


@shared_task
def process_job_application(job_url: str, cv_text: str, cv_file_path: str) -> None:
    """
    Punto de entrada asincrono (Celery) para postular a una oferta.

    Por ahora solo valida que Celery puede levantar Chromium y navegar a la
    URL recibida; el llenado real del formulario se integra en un paso
    posterior.
    """
    try:
        with sync_playwright() as playwright:
            context = FormAutomation.start_persistent_browser(playwright, headless=False)
            page = context.new_page()
            page.goto(job_url)

            print(f"Iniciando postulación en: {job_url}")
            page.wait_for_timeout(3000)

            context.close()
    except PlaywrightError as exc:
        print(f"[ERROR] Fallo de Playwright al procesar '{job_url}': {exc}")
