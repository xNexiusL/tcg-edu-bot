
import os
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


def get_booster_url():
    url = os.getenv("TCG_BOOSTER_URL", "").strip()
    site_url = os.getenv("TCG_URL", "").strip()

    parsed = urlparse(url)
    site = urlparse(site_url)

    if (
        parsed.scheme != "https"
        or parsed.hostname != site.hostname
        or not parsed.hostname
    ):
        raise ValueError(
            "TCG_BOOSTER_URL doit être une URL HTTPS "
            "du même domaine que TCG_URL."
        )

    return url


BOOSTER_COUNT_SELECTOR = os.getenv(
    "BOOSTER_COUNT_SELECTOR", ""
).strip()

BOOSTER_ITEM_SELECTOR = os.getenv(
    "BOOSTER_ITEM_SELECTOR", ""
).strip()

BOOSTER_READY_SELECTOR = os.getenv(
    "BOOSTER_READY_SELECTOR", ""
).strip()
