"""Database updating functions for entire MTG sets"""

import sys
from typing import Dict, List

from pdh_json_updater.scryfall_fetcher import ScryfallFetcher
from pdh_json_updater.file_handler import FileHandler
from pdh_json_updater.legality import Legality
from pdh_json_updater.json_card import JsonCard

# search for cards of rarity less than r and set of...
SCRYFALL_SET_SEARCH_URL = "https://api.scryfall.com/cards/search?q=r%3Cr+set%3A{0}{1}"
# looks like scryfall api responses don't include specific 'type', just 'type line' so we can parse each card to check or...only search good ones
# Adding stickers to the top level here so I don't have to add manually
CARDTYPE_SEARCH_MODIFIER = "+in%3Apaper+(legal%3Avintage+OR+restricted%3Avintage+OR+banned%3Avintage+OR+t%3AStickers+OR+t%3Aattraction)"


def fetch_set(set_code: str) -> List:
    """Fetches an entire set of cards from Scryfall given the search url, and returns them as an array"""
    url = SCRYFALL_SET_SEARCH_URL.format(set_code, CARDTYPE_SEARCH_MODIFIER)
    print(f"Attempting to fetch set {set_code}...", end=" ")

    scryfall_result = ScryfallFetcher.fetch_data(url, raise_exceptions=False)
    if not scryfall_result.was_successful:
        print(
            f"\nERROR: Couldn't fetch {set_code}, skipping this set. Reason: {scryfall_result.error_message}"
        )
        return []

    print("Done.")
    return scryfall_result.data


def update_json_with_set(set_code: str, existing_commander_json: Dict[str, JsonCard]):
    """Given a set code and a dict with legality info, updates that dict with legality of cards from that set."""
    # fetches requested set as an array of card objects
    mtg_set = fetch_set(set_code)
    # transforms each card in mtg_set and adds them to a "format_additions" to be merged with master list
    for card in mtg_set:
        json_card = JsonCard(card)
        card_oracle_id = json_card.scryfallOracleId

        # if this is first printing, add to list. If this is a reprint, requires a little extra checking
        # if card["reprint"]: <- much cleaner, but only works if sets added chronologically since first printing, reprint = false
        if (
            json_card.legality != Legality.NOT_LEGAL.value
            or json_card.isPauperCommander
        ):
            if card_oracle_id in existing_commander_json:
                prev_card_ruling = existing_commander_json[card_oracle_id]
                if json_card.legality == Legality.LEGAL.value:
                    prev_card_ruling.legality = Legality.LEGAL.value
                # update pauper commander status
                if json_card.isPauperCommander:
                    prev_card_ruling.isPauperCommander = True
            else:
                existing_commander_json[card_oracle_id] = json_card


# ------------------------
def main():
    """Primary entrypoint for add-set script"""
    if len(sys.argv) != 2:  # The script itself is the first argument.
        print(
            f"ERROR: Incorrect arguments.\n"
            f"Correct usage: {sys.argv[0]} <set_code>\n"
            f"Example: {sys.argv[0]} m21"
        )
        return

    set_code = sys.argv[1]
    existing_json = FileHandler.get_existing_json()
    update_json_with_set(set_code, existing_json)
    FileHandler.save_format_json_to_file(existing_json)


if __name__ == "__main__":
    main()
