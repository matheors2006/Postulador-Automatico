import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

import django

django.setup()

from bot.services.browser_engine import FormAutomation
from bot.services.llm_groq import JobApplicationBrain

load_dotenv()

CV_TEXT = (
    "Soy desarrollador Python y Django con 4 años de experiencia. "
    "Vivo en Lima, Perú. Tengo disponibilidad inmediata y permiso legal "
    "para trabajar. Mi expectativa salarial es $2000."
)


def main() -> None:
    html_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "mock_linkedin_modal.html")
    )
    file_url = "file:///" + html_path.replace("\\", "/")

    dummy_cv_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "dummy_cv.pdf")
    )
    open(dummy_cv_path, "w").close()

    with sync_playwright() as p:
        context = FormAutomation.start_persistent_browser(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(file_url)

        container = page.locator("body")

        form_fields = FormAutomation.extract_form_fields(container)
        print("Campos extraidos:")
        print(form_fields)

        groq_response = JobApplicationBrain.solve_form(CV_TEXT, form_fields)
        print("Respuesta de Groq:")
        print(groq_response)

        FormAutomation.fill_form_fields(container, groq_response, cv_file_path=dummy_cv_path)

        page.wait_for_timeout(5000)
        context.close()


if __name__ == "__main__":
    main()
