
import os
import logging

from playwright.sync_api import TimeoutError as PWTimeout
from modules.pack_animation import PackAnimation
from modules.card_revealer import CardRevealer
from modules.booster_checker import get_available_boosters

logger = logging.getLogger(__name__)


class BoosterCollector:

    def __init__(self, page):
        self.page = page

        self.claim_selector = os.getenv(
            "BOOSTER_CLAIM_SELECTOR",
            "button.v3-open"
        ).strip()

        self.dry_run = (
            os.getenv("TCG_DRY_RUN", "true").lower()
            == "true"
        )

        self.max_claims = int(
            os.getenv("TCG_MAX_CLAIMS", "10")
        )
        print(
            f"[CONFIG] TCG_MAX_CLAIMS = {self.max_claims}",
            flush=True
        )

        self.timeout = 30000

        if not 1 <= self.max_claims <= 100:
            raise ValueError(
                "TCG_MAX_CLAIMS doit être entre 1 et 100"
            )

    def get_button(self):
        buttons = self.page.locator(
            self.claim_selector
        )

        if buttons.count() != 1:
            raise RuntimeError(
                "Bouton Ouvrir absent ou ambigu"
            )

        button = buttons.first

        if not button.is_visible():
            raise RuntimeError(
                "Bouton Ouvrir invisible"
            )

        if not button.is_enabled():
            raise RuntimeError(
                "Bouton Ouvrir désactivé"
            )

        cost = button.locator(
            ".v3-open-cost"
        ).inner_text().strip().lower()

        if cost != "1 gratuit":
            raise RuntimeError(
                f"Coût inattendu : {cost}"
            )

        return button

    def wait_for_counter_decrease(self, previous):
        """Attend une diminution exacte de 1."""

        selector = os.getenv(
            "BOOSTER_COUNT_SELECTOR",
            ".free-ring b"
        )

        try:
            self.page.wait_for_function(
                """({selector, previous}) => {
                    const el =
                        document.querySelector(selector);

                    if (!el) return false;

                    const value = Number(
                        el.textContent.trim()
                    );

                    return Number.isInteger(value)
                        && value === previous - 1;
                }""",
                arg={
                    "selector": selector,
                    "previous": previous
                },
                timeout=self.timeout
            )

        except PWTimeout as error:
            raise RuntimeError(
                "Le compteur n'a pas diminué "
                "comme attendu. Arrêt de sécurité."
            ) from error


    def close_results(self):
        """Ferme l'écran de résultats du booster."""

        summary = self.page.locator(
            ".opening-stage--summary"
        )

        summary.wait_for(
            state="visible",
            timeout=15000
        )

        # Chercher le bouton Fermer dans toute la page.
        close_buttons = self.page.locator(
            'button.icon-btn[aria-label="Fermer"]'
        )

        print(
            "[COLLECTOR] Boutons Fermer trouvés :",
            close_buttons.count(),
            flush=True
        )

        if close_buttons.count() != 1:
            raise RuntimeError(
                "Impossible d'identifier un bouton Fermer unique."
            )

        close_button = close_buttons.first

        if not close_button.is_visible():
            raise RuntimeError(
                "Le bouton Fermer est présent mais invisible."
            )

        print(
            "[COLLECTOR] Clic sur Fermer...",
            flush=True
        )

        close_button.click(
            timeout=10000
        )

        # Vérifier que l'écran de résultats disparaît.
        summary.wait_for(
            state="hidden",
            timeout=15000
        )

        print(
            "[COLLECTOR] Résultats fermés avec succès !",
            flush=True
        )


    def wait_until_ready(self):
        """Attend que le bouton soit de nouveau prêt."""

        try:
            self.page.locator(
                self.claim_selector
            ).wait_for(
                state="visible",
                timeout=self.timeout
            )

            self.page.wait_for_function(
                """selector => {
                    const buttons =
                        document.querySelectorAll(selector);

                    if (buttons.length !== 1)
                        return false;

                    const button = buttons[0];

                    return !button.disabled
                        && button.getAttribute(
                            "aria-disabled"
                        ) !== "true";
                }""",
                arg=self.claim_selector,
                timeout=self.timeout
            )

        except PWTimeout as error:
            raise RuntimeError(
                "Bouton non disponible après "
                "l'animation."
            ) from error


    def collect(self):
        """Ouvre les boosters gratuits jusqu'à épuisement du stock."""

        available = get_available_boosters(self.page)

        print(
            f"[COLLECTOR] Boosters disponibles : {available}",
            flush=True
        )

        if available <= 0:
            print(
                "[COLLECTOR] Aucun booster gratuit disponible.",
                flush=True
            )
            return 0

        # Vérifier que le bouton utilise bien un booster gratuit.
        self.get_button()

        if self.dry_run:
            print(
                "[COLLECTOR] Mode simulation : aucune ouverture.",
                flush=True
            )
            return 0

        opened = 0

        while opened < self.max_claims:

            print(
                f"[DEBUG] Nouvelle itération : "
                f"opened={opened}, max_claims={self.max_claims}",
                flush=True
            )  

            
            # Lire le stock avant chaque ouverture.
            before = get_available_boosters(self.page)

            if before <= 0:
                print(
                    "[COLLECTOR] Stock épuisé : arrêt.",
                    flush=True
                )
                break

            print(
                f"[COLLECTOR] Ouverture {opened + 1} "
                f"| Stock restant : {before}",
                flush=True
            )

            print(
                "[DEBUG] Attente du prochain booster...",
                flush=True
            )
            # Attendre que la page soit prête.
            self.wait_until_ready()

            print(
                "[DEBUG] Bouton du prochain booster prêt.",
                flush=True
            )

            # Vérifier que le booster est toujours gratuit.
            button = self.get_button()

            # Ouvrir le booster.
            button.click(timeout=10000)

            print(
                "[COLLECTOR] Bouton Ouvrir cliqué.",
                flush=True
            )

            # Déchirer le paquet.
            animation = PackAnimation(self.page)
            animation.open_pack()

            print(
                "[COLLECTOR] Paquet déchiré.",
                flush=True
            )

            # Révéler les cinq cartes.
            revealer = CardRevealer(self.page)
            revealer.reveal_cards()

            print(
                "[COLLECTOR] Cinq cartes traitées.",
                flush=True
            )

            # Confirmer qu'un booster gratuit a été consommé.
            self.wait_for_counter_decrease(before)

            print(
                f"[COLLECTOR] Booster confirmé : "
                f"{before} -> {before - 1}",
                flush=True
            )

            # Fermer l'écran de résultats.
            self.close_results()

            opened += 1

            print(
                f"[COLLECTOR] Total ouvert : {opened}",
                flush=True
            )

            # Vérifier le stock après fermeture.
            remaining = get_available_boosters(self.page)

            print(
                f"[DEBUG] Compteur après fermeture = {remaining}",
                flush=True
            )
            if remaining <= 0:
                print(
                    "[COLLECTOR] Tous les boosters gratuits "
                    "ont été ouverts !",
                    flush=True
                )
                break

            print(
                f"[DEBUG] Stock après fermeture : {remaining}",
                flush=True
            )

            print(
                f"[DEBUG] Boosters ouverts : {opened}",
                flush=True
            )

            print(
                f"[DEBUG] Limite configurée : {self.max_claims}",
                flush=True
            )

            print(
                "[DEBUG] Boutons Ouvrir trouvés :",
                self.page.locator(self.claim_selector).count(),
                flush=True
            )

            print(
                "[DEBUG] Bouton Ouvrir visible :",
                self.page.locator(self.claim_selector).first.is_visible()
                if self.page.locator(self.claim_selector).count() > 0
                else False,
                flush=True
            )

            print(
                f"[COLLECTOR] Il reste {remaining} "
                "boosters gratuits.",
                flush=True
            )

        print(
            f"[COLLECTOR] Collecte terminée : "
            f"{opened} booster(s) ouvert(s).",
            flush=True
        )

        return opened
