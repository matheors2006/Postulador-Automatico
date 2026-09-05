import os

from celery import shared_task
from django.conf import settings
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from bot.models import CandidateProfile
from bot.services.browser_engine import FormAutomation
from bot.services.cv_parser import extract_text_from_pdf
from bot.services.llm_groq import JobApplicationBrain

MAX_APPLY_STEPS = 10

NEXT_BUTTON_SELECTOR = (
    'button:has-text("Siguiente"), button:has-text("Next"), '
    'button:has-text("Revisar"), button:has-text("Review")'
)
SUBMIT_BUTTON_SELECTOR = (
    'button:has-text("Enviar solicitud"), button:has-text("Submit application")'
)


def _prepare_job_url(job_url: str) -> str:
    """
    Limpia parametros de rastreo y, si es una oferta de LinkedIn, fuerza la
    ruta '/apply/' para que el modal de Easy Apply se abra directamente al
    navegar, sin depender de hacer clic en el boton.
    """
    clean_url = job_url.split("?")[0]

    if "linkedin.com/jobs/view/" in clean_url:
        if not clean_url.endswith("/"):
            clean_url += "/"
        if not clean_url.endswith("apply/"):
            clean_url += "apply/"

    return clean_url


@shared_task
def process_job_application(job_url: str, cv_file_path: str) -> None:
    """
    Punto de entrada asincrono (Celery) para postular a una oferta: navega
    a la oferta, abre el modal de Easy Apply y recorre sus pasos
    (Siguiente -> Siguiente -> Enviar) resolviendo cada uno con el LLM.
    """
    job_url = _prepare_job_url(job_url)

    relative_cv_path = os.path.relpath(cv_file_path, settings.MEDIA_ROOT)
    try:
        profile = CandidateProfile.objects.get(cv_file=relative_cv_path)
        extra_instructions = profile.extra_instructions
    except CandidateProfile.DoesNotExist:
        extra_instructions = ""

    cv_text = extract_text_from_pdf(cv_file_path)

    try:
        with sync_playwright() as playwright:
            context = FormAutomation.start_persistent_browser(playwright, headless=False)
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(job_url)

            print(f"Iniciando postulación en: {job_url}")

            modal = page.locator(".jobs-easy-apply-modal")
            try:
                modal.wait_for(state="visible", timeout=15000)
            except PlaywrightTimeoutError:
                print(f"[WARN] El modal de Easy Apply no apareció para '{job_url}'.")
                context.close()
                return

            attempts = 0
            while True:
                attempts += 1
                if attempts > MAX_APPLY_STEPS:
                    print(
                        f"[WARN] Se alcanzó el máximo de {MAX_APPLY_STEPS} "
                        f"pasos sin enviar la postulación a '{job_url}'."
                    )
                    break

                form_fields = FormAutomation.extract_form_fields(modal)

                if form_fields:
                    groq_response = JobApplicationBrain.solve_form(
                        cv_text, form_fields, extra_instructions
                    )
                    FormAutomation.fill_form_fields(modal, groq_response, cv_file_path)

                next_button = modal.locator(NEXT_BUTTON_SELECTOR).first
                if next_button.is_visible():
                    next_button.click()
                    page.wait_for_timeout(2500)
                    continue

                submit_button = modal.locator(SUBMIT_BUTTON_SELECTOR).first
                if submit_button.is_visible():
                    submit_button.click()
                    page.wait_for_timeout(3000)
                    print("¡Postulación enviada con éxito!")
                    break

                print(
                    "[WARN] No se encontró botón de 'Siguiente' ni de "
                    "'Enviar'. Deteniendo el flujo (¿formulario atascado?)."
                )
                break

            context.close()
    except PlaywrightError as exc:
        print(f"[ERROR] Fallo de Playwright al procesar '{job_url}': {exc}")
