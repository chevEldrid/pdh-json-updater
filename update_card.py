import sys
from typing import Dict

from file_handler import FileHandler
from legality import Legality
from json_card import JsonCard

def update_card_in_json(card_name: str, updated_legality: str, existing_format_json: Dict[str, JsonCard]):
    """Given a card name, its new legality, and a dict with legality info, updates the entry for that card in that dict."""
    if card_name in existing_format_json:
        prev_card_ruling = existing_format_json[card_name]
        if updated_legality in Legality:
            prev_card_ruling.legality = updated_legality
            print("Card object updated!")
        else:
            print("ERROR: illegal rarity provided")
    else:
        print("ERROR: "+card_name+" not found in existing commander json")


def main():
    try:
        card_name = sys.argv[1]
        updated_legality = sys.argv[2]
    except:
        print("ERROR: Requires both a card name and legality")
        return

    format_json = FileHandler.get_existing_json()
    update_card_in_json(card_name, updated_legality, format_json)
    FileHandler.save_format_json_to_file(format_json)


if __name__ == "__main__":
    main()
