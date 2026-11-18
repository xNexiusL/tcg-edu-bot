
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT_DIR = Path(
    r"C:\AA GSIMMF Database\NHTC Experimental\tcg-bot"
)

PROFILE_DIR = PROJECT_DIR / "data" / "browser_profile"


def start_browser():
    PROFILE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    playwright = sync_playwright().start()

    try:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={
                "width": 1366,
                "height": 768
            },
            accept_downloads=False
        )

        page = (
            context.pages[0]
            if context.pages
            else context.new_page()
        )

        return playwright, context, page

    except Exception:
        playwright.stop()
        raise


def stop_browser(playwright, context):
    try:
        context.close()
    finally:
        playwright.stop()
