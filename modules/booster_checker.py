
import re
import logging

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config import (
    get_booster_url,
    BOOSTER_COUNT_SELECTOR,
    BOOSTER_ITEM_SELECTOR,
    BOOSTER_READY_SELECTOR
)

logger = logging.getLogger(__name__)


class BoosterDetectionError(Exception):
    pass


def open_booster_page(page):
    """Ouvre la page des boosters."""

    url = get_booster_url()

    logger.info("Ouverture de la page boosters")

    page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=30000
    )

    if BOOSTER_READY_SELECTOR:
        page.locator(
            BOOSTER_READY_SELECTOR
        ).wait_for(
            state="visible",
            timeout=15000
        )

    logger.info("Page boosters chargée")


def read_booster_counter(page):
    """Lit le compteur affiché sur le site."""

    if not BOOSTER_COUNT_SELECTOR:
        return None

    element = page.locator(
        BOOSTER_COUNT_SELECTOR
    )

    try:
        element.first.wait_for(
            state="visible",
            timeout=10000
        )
    except PlaywrightTimeoutError as error:
        raise BoosterDetectionError(
            "Compteur introuvable"
        ) from error

    if element.count() != 1:
        raise BoosterDetectionError(
            "Le sélecteur du compteur doit "
            "correspondre à un seul élément"
        )

    text = element.inner_text().strip()

    # Accepte "3" ou "3 boosters disponibles"
    match = re.search(r"\d+", text)

    if not match:
        raise BoosterDetectionError(
            f"Compteur non numérique : {text!r}"
        )

    return int(match.group())


def count_booster_elements(page):
    """Compte les boosters disponibles."""

    if not BOOSTER_ITEM_SELECTOR:
        return None

    elements = page.locator(
        BOOSTER_ITEM_SELECTOR
    )

    return elements.count()


def get_available_boosters(page):
    """Retourne le nombre de boosters disponibles."""

    counter = read_booster_counter(page)
    items = count_booster_elements(page)

    if counter is None and items is None:
        raise BoosterDetectionError(
            "Aucune méthode de détection configurée"
        )

    if counter is not None and items is not None:
        if counter != items:
            raise BoosterDetectionError(
                "Incohérence : compteur="
                f"{counter}, éléments={items}"
            )

    available = (
        counter if counter is not None else items
    )

    logger.info(
        "Boosters disponibles : %s",
        available
    )

    return available
