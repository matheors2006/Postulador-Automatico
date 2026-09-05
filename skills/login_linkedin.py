import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django

django.setup()

from django.conf import settings
from playwright.sync_api import sync_playwright

PLAYWRIGHT_PROFILE_DIR = os.path.join(settings.BASE_DIR, "playwright_profile")


def main() -> None:
    os.makedirs(PLAYWRIGHT_PROFILE_DIR, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PLAYWRIGHT_PROFILE_DIR,
            headless=False,
            no_viewport=True,
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://www.linkedin.com/login")

        input(
            "Inicia sesión manualmente en la ventana del navegador. Cuando "
            "veas el feed principal de LinkedIn, presiona ENTER en esta "
            "consola para guardar la sesión..."
        )

        context.close()


if __name__ == "__main__":
    main()
