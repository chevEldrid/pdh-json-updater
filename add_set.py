import sys
import requests
import jsonpickle
import time
from typing import Dict

from file_handler import FileHandler
from legality import Legality
from json_card import JsonCard

# search for cards of rarity less than r and set of...
SCRYFALL_SET_SEARCH_URL = "https://api.scryfall.com/cards/search?q=r%3Cr+set%3A{0}{1}"
# looks like scryfall api responses don't include specific 'type', just 'type line' so we can parse each card to check or...only search good ones
CARDTYPE_SEARCH_MODIFIER = "+in%3Apaper+(legal%3Avintage+OR+restricted%3Avintage+OR+banned%3Avintage)"

# Fetches an entire set of cards from Scryfall given the search url, and returns them as an array
def fetch_set(set_code):
    total_set = []
    url = SCRYFALL_SET_SEARCH_URL.format(
        set_code, CARDTYPE_SEARCH_MODIFIER)
    print("attempting to fetch set")
    try:
        while True:
            r = requests.get(url)
            x = jsonpickle.loads(r.text)
            total_set.extend(x["data"])
            if x["has_more"]:
                url = x["next_page"]
                time.sleep(.15)
            else:
                break
    except:
        print("Error attempting to grab set "+set_code+", skipping.")

    return total_set


def update_json_with_set(set_code, existing_commander_json: Dict[str, JsonCard]):
    """Given a set code and a dict with legality info, updates that dict with legality of cards from that set."""
    # fetches requested set as an array of card objects
    mtg_set = fetch_set(set_code)
    # transforms each card in mtg_set and adds them to a "format_additions" to be merged with master list
    for card in mtg_set:
        json_card = JsonCard(card)
        card_name = json_card.name

        if json_card.legality != Legality.NOT_LEGAL:
            # if this is first printing, add to list. If this is a reprint, requires a little extra checking
            # if card["reprint"]: <- much cleaner, but only works if sets added chronologically since first printing, reprint = false
            if card_name in existing_commander_json:
                prev_card_ruling = existing_commander_json[card_name]
                if prev_card_ruling.legality == Legality.LEGAL_AS_COMMANDER and json_card.legality == Legality.LEGAL:
                    prev_card_ruling.legality = Legality.LEGAL
            else:
                existing_commander_json[card_name] = json_card


# ------------------------
def main():
    try:
        set_code = sys.argv[1]
    except:
        print("ERROR: Set code must be provided")
        sys.exit()

    existing_json = FileHandler.get_existing_json()
    update_json_with_set(set_code, existing_json)
    FileHandler.save_format_json_to_file(existing_json)


if __name__ == "__main__":
    main()
