
from playwright.sync_api import TimeoutError as PWTimeout


class CardRevealer:

    def __init__(self, page):
        self.page = page

        self.pile = page.locator(".pile")
        self.hidden = page.locator(".pile .pile-card")
        self.flipped = page.locator(".pile .flip.is-flipped")
        self.tray = page.locator(".tray .tray-card")
        self.special = page.locator(
            ".pile .flip.flip--or"
        )
        self.final_card = page.locator(
            ".pile > .flip"
        )
    def reveal_cards(self):
        """Révèle les cartes et vérifie leur rangement."""

        self.pile.wait_for(
            state="visible",
            timeout=15000
        )

        initial_tray = self.tray.count()

        print(
            f"[CARDS] Cartes déjà rangées : {initial_tray}",
            flush=True
        )

        if initial_tray > 5:
            raise RuntimeError(
                "Nombre inattendu de cartes rangées."
            )

        while self.tray.count() < 5:
            if self.tray.count() == 4:
                self.reveal_final_card()

                print(
                    "[CARDS] Les cinq cartes ont été traitées.",
                    flush=True
                )

                return 5 - initial_tray
            before_tray = self.tray.count()
            print(
                "[CARDS DEBUG] Cartes cachées :",
                self.hidden.count(),
                flush=True
            )

            print(
                "[CARDS DEBUG] Cartes retournées :",
                self.flipped.count(),
                flush=True
            )

            print(
                "[CARDS DEBUG] Cartes rangées :",
                self.tray.count(),
                flush=True
            )

            print(
                f"[CARDS] Traitement de la carte "
                f"{before_tray + 1}/5",
                flush=True
            )

            # ÉTAPE 1 : retourner la carte si nécessaire.
            if self.flipped.count() == 0:

                if self.hidden.count() == 0:
                    raise RuntimeError(
                        "Aucune carte cachée disponible."
                    )

                self.hidden.last.click(
                    button="left",
                    force=True,
                    timeout=5000
                )

                print(
                    "[CARDS] Premier clic effectué.",
                    flush=True
                )

                try:
                    self.flipped.wait_for(
                        state="visible",
                        timeout=10000
                    )

                except PWTimeout as error:
                    raise RuntimeError(
                        "La carte ne s'est pas retournée."
                    ) from error

            print(
                "[CARDS] Carte affichée de face.",
                flush=True
            )

            # ÉTAPE 2 : envoyer la carte dans la rangée.
            self.flipped.click(
                button="left",
                force=True,
                timeout=5000
            )

            print(
                "[CARDS] Deuxième clic effectué.",
                flush=True
            )

            # ÉTAPE 3 : confirmer que la rangée a grandi.
            try:
                self.page.wait_for_function(
                    """previous => {
                        return document.querySelectorAll(
                            ".tray .tray-card"
                        ).length === previous + 1;
                    }""",
                    arg=before_tray,
                    timeout=10000
                )

            except PWTimeout as error:
                raise RuntimeError(
                    "La carte n'a pas été ajoutée "
                    "à la rangée. Arrêt de sécurité."
                ) from error

            print(
                f"[CARDS] Carte rangée : "
                f"{self.tray.count()}/5",
                flush=True
            )

        if self.tray.count() != 5:
            raise RuntimeError(
                "Ouverture incomplète : "
                "les cinq cartes ne sont pas rangées."
            )

        print(
            "[CARDS] Les cinq cartes sont rangées !",
            flush=True
        )

        return self.tray.count() - initial_tray
    



    def reveal_final_card(self):
        """Retourne la cinquième carte et attend les résultats."""

        final_card = self.page.locator(".pile > .flip")

        if final_card.count() != 1:
            raise RuntimeError(
                "Dernière carte absente ou ambiguë."
            )

        if self.tray.count() != 4:
            raise RuntimeError(
                "La rangée doit contenir quatre cartes."
            )

        print(
            "[FINAL] Cinquième carte détectée.",
            flush=True
        )

        # ÉTAPE 1 : retourner la cinquième carte.
        if "is-flipped" not in (
            final_card.get_attribute("class") or ""
        ):
            final_card.click(
                button="left",
                force=True,
                timeout=5000
            )

            print(
                "[FINAL] Premier clic effectué.",
                flush=True
            )

        # ÉTAPE 2 : attendre que la carte soit retournée.
        try:
            self.page.locator(
                ".pile > .flip.is-flipped"
            ).wait_for(
                state="visible",
                timeout=15000
            )

        except PWTimeout as error:
            raise RuntimeError(
                "La cinquième carte ne s'est pas retournée."
            ) from error

        print(
            "[FINAL] Cinquième carte retournée.",
            flush=True
        )

        # ÉTAPE 3 : deuxième clic pour terminer l'ouverture.
        final_card.click(
            button="left",
            force=True,
            timeout=5000
        )

        print(
            "[FINAL] Deuxième clic effectué.",
            flush=True
        )

        # ÉTAPE 4 : attendre l'écran de résultats.
        try:
            self.page.locator(
                ".opening-stage--summary"
            ).wait_for(
                state="visible",
                timeout=15000
            )

        except PWTimeout as error:
            raise RuntimeError(
                "L'écran de résultats n'est pas apparu "
                "après la cinquième carte."
            ) from error

        print(
            "[FINAL] Écran de résultats confirmé !",
            flush=True
        )
