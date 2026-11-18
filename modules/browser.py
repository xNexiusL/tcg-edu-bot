
import os
import logging
from pathlib import Path

from playwright.sync_api import sync_playwright

from modules.browser_detector import detect_default_browser


logger = logging.getLogger(__name__)


# Navigateurs Chromium officiellement pris en charge
# via leurs canaux Playwright.
BROWSER_CHANNELS = {
    "msedge": "msedge",
    "chrome": "chrome",
}

# Navigateurs Chromium tiers :
# lancement possible, mais compatibilité non garantie.
THIRD_PARTY_BROWSERS = (
    "brave",
    "opera",
    "vivaldi",
    "chromium",
)


def get_profile_dir(browser_name):
    """
    Crée un profil dédié à TCGBot.

    Les données sont stockées dans AppData,
    indépendamment du dossier du logiciel.
    """

    local_appdata = os.getenv("LOCALAPPDATA")

    if local_appdata:
        base_dir = Path(local_appdata)
    else:
        base_dir = (
            Path.home()
            / "AppData"
            / "Local"
        )

    profile_dir = (
        base_dir
        / "TCGBot"
        / "profiles"
        / browser_name
    )

    profile_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    return profile_dir


def get_default_browser_candidate():
    """
    Identifie le navigateur Windows par défaut.

    Retourne un candidat Chromium ou None.
    """

    info = detect_default_browser()

    logger.info(
        "Navigateur Windows détecté : %s",
        info.get("progid")
    )

    executable = info.get("executable")
    engine = info.get("engine")

    if not executable or engine != "chromium":
        logger.info(
            "Navigateur par défaut non compatible "
            "avec le moteur Chromium."
        )
        return None

    executable_path = Path(executable)

    if not executable_path.is_file():
        logger.warning(
            "Exécutable introuvable : %s",
            executable
        )
        return None

    browser_name = executable_path.stem.lower()

    # Edge et Chrome utilisent leurs canaux officiels.
    if browser_name in BROWSER_CHANNELS:
        return {
            "name": browser_name,
            "channel": BROWSER_CHANNELS[browser_name],
            "executable_path": None,
        }

    # Les autres navigateurs Chromium sont lancés
    # directement depuis leur exécutable.
    if any(
        name in browser_name
        for name in THIRD_PARTY_BROWSERS
    ):
        return {
            "name": browser_name,
            "channel": None,
            "executable_path": str(executable_path),
        }

    logger.warning(
        "Navigateur Chromium non reconnu : %s",
        browser_name
    )

    return None


def get_browser_candidates():
    """
    Construit la liste des navigateurs à essayer :

    1. Navigateur Windows par défaut compatible
    2. Microsoft Edge
    3. Google Chrome
    """

    candidates = []

    default_candidate = get_default_browser_candidate()

    if default_candidate:
        candidates.append(default_candidate)

    fallbacks = [
        {
            "name": "msedge",
            "channel": "msedge",
            "executable_path": None,
        },
        {
            "name": "chrome",
            "channel": "chrome",
            "executable_path": None,
        },
    ]

    # Évite de tester deux fois le même navigateur.
    existing_names = {
        candidate["name"]
        for candidate in candidates
    }

    for candidate in fallbacks:
        if candidate["name"] not in existing_names:
            candidates.append(candidate)

    return candidates


def launch_browser_context(playwright, candidate, headless):
    """
    Lance un navigateur avec un profil persistant.
    """

    name = candidate["name"]
    profile_dir = get_profile_dir(name)

    launch_options = {
        "user_data_dir": str(profile_dir),
        "headless": headless,
        "viewport": {
            "width": 1366,
            "height": 768,
        },
        "accept_downloads": False,
    }

    if candidate["channel"]:
        launch_options["channel"] = candidate["channel"]

    if candidate["executable_path"]:
        launch_options["executable_path"] = (
            candidate["executable_path"]
        )

    logger.info(
        "Tentative de lancement : %s",
        name
    )

    return (
        playwright.chromium.launch_persistent_context(
            **launch_options
        )
    )


def start_browser():
    """
    Démarre le navigateur Windows par défaut
    lorsqu'il est compatible.

    Sinon, utilise Edge puis Chrome.

    Compatible avec l'interface existante :
        playwright, context, page = start_browser()
    """

    headless = (
        os.getenv("HEADLESS", "false")
        .strip()
        .lower() == "true"
    )

    candidates = get_browser_candidates()

    playwright = sync_playwright().start()

    context = None
    last_error = None

    try:
        for candidate in candidates:
            try:
                context = launch_browser_context(
                    playwright,
                    candidate,
                    headless
                )

                page = (
                    context.pages[0]
                    if context.pages
                    else context.new_page()
                )

                logger.info(
                    "Navigateur utilisé : %s",
                    candidate["name"]
                )

                return playwright, context, page

            except Exception as error:
                last_error = error

                logger.warning(
                    "Échec du navigateur %s : %s",
                    candidate["name"],
                    error
                )

        raise RuntimeError(
            "Impossible de démarrer un navigateur "
            "compatible. Vérifiez que Microsoft Edge "
            "ou Google Chrome est installé."
        ) from last_error

    except Exception:
        if context is not None:
            try:
                context.close()
            except Exception:
                pass

        playwright.stop()
        raise


def stop_browser(playwright, context):
    """
    Ferme proprement le navigateur et Playwright.
    """

    try:
        if context is not None:
            context.close()

    finally:
        if playwright is not None:
            playwright.stop()
