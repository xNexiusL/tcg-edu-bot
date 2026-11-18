
import os
import logging

from dotenv import load_dotenv

from inspect_cards import inspect_cards

from modules.browser import (
    start_browser,
    stop_browser
)

from modules.booster_checker import (
    open_booster_page
)

from modules.booster_collector import (
    BoosterCollector
)


def main():
    # Charger le .env en donnant priorité à ses valeurs.
    load_dotenv(override=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(message)s"
    )

    print(
        "[CONFIG] TCG_MAX_CLAIMS depuis .env :",
        os.getenv("TCG_MAX_CLAIMS"),
        flush=True
    )

    print(
        "[CONFIG] TCG_DRY_RUN :",
        os.getenv("TCG_DRY_RUN"),
        flush=True
    )

    playwright = None
    context = None

    try:
        playwright, context, page = start_browser()

        open_booster_page(page)

        collector = BoosterCollector(page)

        # Ouvrir les boosters gratuits.
        collector.collect()

        print(
            "[DEBUG] Collecte terminée.",
            flush=True
        )

        # Diagnostic des cartes affichées.
        inspect_cards(page)

        print(
            "[DEBUG] Diagnostic terminé.",
            flush=True
        )

    except Exception as error:
        logging.exception(
            "Erreur pendant la collecte : %s",
            error
        )

    finally:
        if playwright is not None:
            input("Entrée pour fermer...")
            stop_browser(playwright, context)


if __name__ == "__main__":
    main()
