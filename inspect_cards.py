
def inspect_cards(page):
    """Affiche l'état du tas de cartes sans cliquer."""

    selectors = {
        "Cartes cachées": ".pile .pile-card",
        "Cartes retournées": ".pile .flip.is-flipped",
        "Cartes en cours de retournement": ".pile .flip:not(.is-flipped)",
        "Tas central": ".pile",
    }

    print("\n===== ÉTAT DES CARTES =====")

    for label, selector in selectors.items():
        count = page.locator(selector).count()
        print(f"{label} : {count}")

    print("==========================\n")
