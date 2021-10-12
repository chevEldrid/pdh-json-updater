import os
import sys
import requests
import json
import time
from datetime import date

set_code = ""
# json object storing final dump
format_json = {}
# existing json rulings loaded in from RESULT_FILE
existing_json = {}

RESULT_FILE = "pauper-commander.json"
# search for cards of rarity less than r and set of...
SCRYFALL_SET_SEARCH_URL = "https://api.scryfall.com/cards/search?q=r%3Cr+set%3A{0}{1}"
# looks like scryfall api responses don't include specific 'type', just 'type line' so we can parse each card to check or...only search good ones
CARDTYPE_SEARCH_MODIFIER = "+in%3Apaper+legal%3Avintage"

PDH_BANLIST = ["Rhystic Study", "Mystic Remora"]
CULTURAL_BANLIST = ["Stone-Throwing Devils", "Pradesh Gypsies"]

LEGAL = "Legal"
LEGAL_AS_COMMANDER = "Legal As Commander"
NOT_LEGAL = "Not Legal"
# transforms a scryfall card object into a json card object


def card_to_json(card):
    return {
        "scryfallOracleId": card["oracle_id"],
        "name": card["name"],
        "legality": is_legal(card)
    }

# determines legality of a card based on rarity (legal, legal as commander, not legal) and banlist


def is_legal(card):
    joint_banlist = PDH_BANLIST + CULTURAL_BANLIST
    # check for bannings
    if card["name"] in joint_banlist:
        return NOT_LEGAL
    # check rarity
    if card["rarity"] == "common":
        return LEGAL
    elif card["rarity"] == "uncommon" and "Creature" in card["type_line"]:
        return LEGAL_AS_COMMANDER
    else:
        return NOT_LEGAL

# Fetches an entire set of cards from Scryfall given the search url, and returns them as an array


def fetch_set(set_code):
    total_set = []
    has_more = False
    url = SCRYFALL_SET_SEARCH_URL.format(
        set_code, CARDTYPE_SEARCH_MODIFIER)

    while not has_more:
        has_more = False
        r = requests.get(url)
        x = json.loads(r.text)
        total_set.append(x["data"])

        if x["has_more"]:
            url = x["next_page"]
            has_more = True
            time.sleep(.15)

    return total_set


# ------------------------
try:
    set_code = sys.argv[1]
except:
    print("ERROR: Set code must be provided")
    sys.exit()

# fetches existing list of cards
if os.path.exists(RESULT_FILE):
    with open(RESULT_FILE) as card_file:
        data = json.load(card_file)
        for card in data:
            existing_json[card["name"]] = card
else:
    os.mknod(RESULT_FILE)

# fetches requested set as an array of card objects
mtg_set = fetch_set(set_code)
# transforms each card in mtg_set and adds them to a "format_additions" to be merged with master list
for card in mtg_set[0]:
    json_card = card_to_json(card)
    card_name = card["name"]

    if json_card["legality"] == LEGAL or json_card["legality"] == LEGAL_AS_COMMANDER:
        # if this is first printing, add to list. If this is a reprint, requires a little extra checking
        # if card["reprint"]: <- much cleaner, but only works if sets added chronologically since first printing, reprint = false
        if card_name in existing_json:
            prev_card_ruling = existing_json[card_name]
            if prev_card_ruling["legality"] == LEGAL_AS_COMMANDER and json_card["legality"] == LEGAL:
                prev_card_ruling["legality"] = LEGAL
        else:
            format_json[card_name] = json_card

format_list = list(format_json.values()) + list(existing_json.values())

format_list.sort(key=lambda x: x['name'], reverse=False)

with open(RESULT_FILE, 'w') as output_file:
    json.dump(format_list, output_file)
