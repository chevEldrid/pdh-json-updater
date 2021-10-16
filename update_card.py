import os
import sys
import jsonpickle
from typing import List, Dict

from add_set import LEGALITIES, JsonCard

RESULT_FILE = "pauper-commander.json"

def update_card(card_name, updated_legality, existing_commander_json):
    if card_name in existing_commander_json:
        prev_card_ruling = existing_commander_json[card_name]
        if updated_legality in LEGALITIES:
            prev_card_ruling.legality = updated_legality
            print("Card object updated!")
        else:
            print("ERROR: illegal rarity provided")
    else:
        print("ERROR: "+card_name+" not found in existing commander json")
    return existing_commander_json


def main():
    try:
        card_name = sys.argv[1]
        updated_legality = sys.argv[2]
    except:
        print("ERROR: Requires both a card name and legality")

    existing_commander_json: Dict[str, JsonCard] = {}
    card_list: List[JsonCard] = []

    if os.path.exists(RESULT_FILE):
        with open(RESULT_FILE) as card_file:
            data = jsonpickle.decode(card_file.read())
            for card in data:
                existing_commander_json[card.name] = card
        
    existing_commander_json = update_card(card_name, updated_legality, existing_commander_json)
    card_list = list(existing_commander_json.values())

    with open(RESULT_FILE, 'w') as output_file:
        full_json_text = jsonpickle.encode(
            value=card_list, indent=2, separators=(",", ": "))
        output_file.write(full_json_text)


if __name__ == "__main__":
    main()