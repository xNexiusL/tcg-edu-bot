
from dotenv import load_dotenv

from modules.browser import (
    start_browser,
    stop_browser
)

from modules.login import (
    open_tcg_site,
    check_session,
    manual_login
)


def main():
    load_dotenv()

    print("=" * 45)
    print("        TCG BOT - VERSION 0.2")
    print("=" * 45)

    playwright = None
    context = None

    try:
        playwright, context, page = start_browser()

        open_tcg_site(page)

        print()
        print("[TCG] Navigateur prêt.")
        print("[TCG] Vérification de la session...")

        status = check_session(page)

        if status is True:
            print("[TCG] Session confirmée.")

        elif status is False:
            print("[TCG] Connexion nécessaire.")
            manual_login(page)

        else:
            print(
                "[TCG] État de connexion inconnu."
            )

            choice = input(
                "Es-tu déjà connecté ? (o/n) : "
            ).strip().lower()

            if choice != "o":
                manual_login(page)

        print()
        print("[TCG] Phase de navigation terminée.")
        print(
            "[TCG] Le module boosters "
            "sera ajouté au prochain TP."
        )

        input(
            "\nAppuie sur Entrée pour quitter..."
        )

    except Exception as error:
        print(f"[ERREUR] {error}")

    finally:
        if playwright is not None:
            stop_browser(playwright, context)

        print("[TCG] Arrêt du programme.")


if __name__ == "__main__":
    main()
