
import os
from urllib.parse import urlparse


def get_site_url():
    url = os.getenv("TCG_URL", "").strip()

    parsed = urlparse(url)

    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.hostname.endswith(".example")
    ):
        raise ValueError(
            "Configure une véritable URL HTTPS "
            "dans le fichier .env"
        )

    return url


def open_tcg_site(page):
    url = get_site_url()

    print("[TCG] Ouverture du site...")

    page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=30000
    )

    print("[TCG] Site ouvert.")


def check_session(page):
    account_url = os.getenv(
        "TCG_ACCOUNT_URL", ""
    ).strip()

    if not account_url:
        return None

    base = urlparse(get_site_url())
    target = urlparse(account_url)

    if (
        target.scheme != "https"
        or target.hostname != base.hostname
    ):
        raise ValueError(
            "La page du compte doit être "
            "sur le même domaine HTTPS."
        )

    page.goto(
        account_url,
        wait_until="domcontentloaded",
        timeout=30000
    )

    print(
        "[TCG] Vérifie que la page du compte "
        "est accessible."
    )

    # Sans indicateur fiable du site,
    # la connexion ne peut pas être confirmée.
    return None


def manual_login(page):
    print()
    print("=== CONNEXION TCG ===")
    print("Connecte-toi dans le navigateur.")
    print("Ne saisis aucun identifiant ici.")
    print()

    input(
        "Une fois connecté, appuie sur Entrée..."
    )

    print(
        "[TCG] Connexion déclarée terminée. "
        "La session sera conservée si le site "
        "le permet."
    )
