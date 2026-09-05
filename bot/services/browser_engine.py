"""
Automatizacion de navegador (Playwright) para extraer y completar
formularios de postulacion (Easy Apply).
"""

import os
from typing import Any

from django.conf import settings
from playwright.sync_api import BrowserContext, Locator, Playwright
from playwright.sync_api import Error as PlaywrightError

PLAYWRIGHT_PROFILE_DIR = os.path.join(settings.BASE_DIR, "playwright_profile")

_EXTRACT_FIELDS_JS = """
(container) => {
    const elements = container.querySelectorAll(
        'input:not([type="hidden"]), textarea, select'
    );
    const results = [];

    elements.forEach((el) => {
        let label = '';

        if (el.id) {
            const labelFor = container.querySelector(`label[for="${el.id}"]`);
            if (labelFor) {
                label = labelFor.textContent.trim();
            }
        }

        if (!label) {
            const parentLabel = el.closest('label');
            if (parentLabel) {
                label = parentLabel.textContent.trim();
            }
        }

        const tagName = el.tagName.toLowerCase();
        const type = tagName === 'input' ? el.type.toLowerCase() : tagName;

        results.push({
            id: el.id || null,
            name: el.name || null,
            type: type,
            label: label,
        });
    });

    return results;
}
"""


_TRUTHY_VALUES = {"yes", "true", "1", "on", "si", "sí"}


def _is_truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in _TRUTHY_VALUES


class FormAutomation:
    """Extrae y completa campos de un formulario de postulacion."""

    @staticmethod
    def start_persistent_browser(
        playwright: Playwright, headless: bool = False
    ) -> BrowserContext:
        """
        Lanza Chromium con un perfil de usuario persistente para conservar
        la sesion (cookies, login) entre ejecuciones y evitar bloqueos de
        login repetidos en sitios como LinkedIn.

        Args:
            playwright: Instancia activa de Playwright (sync_playwright()).
            headless: Si el navegador debe correr sin interfaz grafica.

        Returns:
            El BrowserContext persistente ya lanzado.
        """
        os.makedirs(PLAYWRIGHT_PROFILE_DIR, exist_ok=True)
        return playwright.chromium.launch_persistent_context(
            user_data_dir=PLAYWRIGHT_PROFILE_DIR,
            headless=headless,
            no_viewport=True,
        )

    @staticmethod
    def extract_form_fields(container: Locator) -> list[dict[str, Any]]:
        """
        Extrae todos los campos rellenables dentro de un container (ej. el
        modal de Easy Apply) mediante un unico container.evaluate(),
        evitando ida y vuelta por cada elemento y evitando "fugarse" hacia
        el resto de la pagina (como la barra de busqueda global).

        Args:
            container: Locator de Playwright acotado al modal/formulario a
                analizar.

        Returns:
            Lista de diccionarios con las llaves id, name, type y label.
        """
        return container.evaluate(_EXTRACT_FIELDS_JS)

    @staticmethod
    def fill_form_fields(
        container: Locator, form_data: dict[str, Any], cv_file_path: str = None
    ) -> None:
        """
        Completa el formulario usando las decisiones tomadas por el LLM.

        Args:
            container: Locator de Playwright acotado al modal/formulario a
                completar.
            form_data: Diccionario {id_del_campo: valor_decidido}, tal como
                lo retorna JobApplicationBrain.solve_form.
            cv_file_path: Ruta absoluta al archivo de CV a adjuntar en los
                campos de tipo file. El valor del LLM se ignora para esos
                campos.
        """
        for field_id, value in form_data.items():
            try:
                locator = container.locator(f'#{field_id}')
                tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                input_type = locator.evaluate(
                    "el => el.type ? el.type.toLowerCase() : ''"
                )

                if input_type == "file":
                    if not cv_file_path or not os.path.isfile(cv_file_path):
                        print(
                            f"[WARN] No se pudo adjuntar el archivo para "
                            f"'{field_id}': cv_file_path no existe "
                            f"({cv_file_path!r})"
                        )
                        continue
                    locator.set_input_files(cv_file_path)
                elif tag_name == "select":
                    locator.select_option(str(value))
                elif input_type in ("radio", "checkbox"):
                    if _is_truthy(value):
                        locator.check()
                else:
                    locator.fill(str(value))
            except PlaywrightError as exc:
                print(f"[WARN] No se pudo completar el campo '{field_id}': {exc}")
                continue
