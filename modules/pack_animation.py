
from playwright.sync_api import TimeoutError as PWTimeout


class PackAnimation:

    def __init__(self, page):
        self.page = page
        self.pack_selector = ".opening-stage .pack.pack--idle"

    def open_pack(self):
        """Attend le paquet et effectue un clic gauche."""

        pack = self.page.locator(
            self.pack_selector
        )

        try:
            pack.wait_for(
                state="visible",
                timeout=20000
            )

            print(
                "[PACK] Paquet détecté et prêt.",
                flush=True
            )

            print(
                "[PACK] Dimensions :",
                pack.bounding_box(),
                flush=True
            )

            # Le paquet bouge à cause de son animation.
            # On ignore donc le contrôle de stabilité.
            pack.click(
                button="left",
                force=True,
                timeout=5000
            )

            print(
                "[PACK] Clic effectué.",
                flush=True
            )

        except PWTimeout as error:
            print(
                "[PACK] ÉCHEC DU CLIC :",
                str(error),
                flush=True
            )
            raise
