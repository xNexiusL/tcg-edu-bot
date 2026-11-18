
import logging

from dotenv import load_dotenv

from modules.browser import (
    start_browser,
    stop_browser
)

from modules.booster_checker import (
    open_booster_page,
    get_available_boosters,
    BoosterDetectionError
)


def main():
    load_dotenv()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s"
    )

    playwright = None
    context = None

    try:
        playwright, context, page = start_browser()

        open_booster_page(page)

        print()
        print("=== ANALYSE DES BOOSTERS ===")

        available = get_available_boosters(page)

        print(f"Boosters disponibles : {available}")

        if available > 0:
            print("Des boosters sont récupérables.")
        else:
            print("Aucun booster disponible.")

        print()
        print("Aucune réclamation effectuée.")

    except BoosterDetectionError as error:
        print(f"Erreur de détection : {error}")

    except Exception as error:
        print(f"Erreur : {error}")

    finally:
        if playwright is not None:
            input("Entrée pour fermer le navigateur...")
            stop_browser(playwright, context)


if __name__ == "__main__":
    main()
