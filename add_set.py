import os
import sys
import requests
import jsonpickle
import time

set_code = ""
# json object storing final dump
format_json = {}
# existing json rulings loaded in from RESULT_FILE
existing_json = {}

RESULT_FILE = "pauper-commander.json"
# search for cards of rarity less than r and set of...
SCRYFALL_SET_SEARCH_URL = "https://api.scryfall.com/cards/search?q=r%3Cr+set%3A{0}{1}"
# looks like scryfall api responses don't include specific 'type', just 'type line' so we can parse each card to check or...only search good ones
CARDTYPE_SEARCH_MODIFIER = "+in%3Apaper+(legal%3Avintage+OR+restricted%3Avintage+OR+banned%3Avintage)"

PDH_BANLIST = ["Rhystic Study", "Mystic Remora"]
CULTURAL_BANLIST = ["Stone-Throwing Devils", "Pradesh Gypsies"]
# Cards "banned" due to incorrect rarities, ante, or any other reason
SOFT_BANLIST = ["Spatial Contortion", "Circle of Flame"]
ILLEGAL_CARD_TYPES = ["Conspiracy", "Vanguard", "Scheme"]

LEGAL = "Legal"
LEGAL_AS_COMMANDER = "Legal As Commander"
NOT_LEGAL = "Not Legal"
# transforms a scryfall card object into a json card object


class JsonCard:
    def __init__(self, scryfall_queried_card):
        self.scryfallOracleId = scryfall_queried_card["oracle_id"]
        self.name = scryfall_queried_card["name"]
        self.legality = is_legal(scryfall_queried_card)


# determines legality of a card based on rarity (legal, legal as commander, not legal) and banlist
def is_legal(scryfall_queried_card):
    front_card_face_typeline = scryfall_queried_card["type_line"].split(
        "//")[0]
    joint_banlist = PDH_BANLIST + CULTURAL_BANLIST + SOFT_BANLIST
    # check for bannings
    if scryfall_queried_card["name"] in joint_banlist:
        return NOT_LEGAL
    # check illegal card types
    if front_card_face_typeline in ILLEGAL_CARD_TYPES:
        return NOT_LEGAL
    # check rarity
    if scryfall_queried_card["rarity"] == "common":
        return LEGAL
    elif scryfall_queried_card["rarity"] == "uncommon" and "Creature" in front_card_face_typeline:
        if "Land" in scryfall_queried_card["type_line"]:
            return NOT_LEGAL
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
        x = jsonpickle.loads(r.text)
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
        data = jsonpickle.decode(card_file.read())
        for card in data:
            existing_json[card.name] = card

# fetches requested set as an array of card objects
mtg_set = fetch_set(set_code)
# transforms each card in mtg_set and adds them to a "format_additions" to be merged with master list
for card in mtg_set[0]:
    json_card = JsonCard(card)
    card_name = json_card.name

    if json_card.legality == LEGAL or json_card.legality == LEGAL_AS_COMMANDER:
        # if this is first printing, add to list. If this is a reprint, requires a little extra checking
        # if card["reprint"]: <- much cleaner, but only works if sets added chronologically since first printing, reprint = false
        if card_name in existing_json:
            prev_card_ruling = existing_json[card_name]
            if prev_card_ruling.legality == LEGAL_AS_COMMANDER and json_card.legality == LEGAL:
                prev_card_ruling.legality = LEGAL
        else:
            format_json[card_name] = json_card

format_list = list(format_json.values()) + list(existing_json.values())

format_list.sort(key=lambda x: x.name, reverse=False)

with open(RESULT_FILE, 'w') as output_file:
    full_json_text = jsonpickle.encode(
        value=format_list, indent=2, separators=(",", ": "))
    output_file.write(full_json_text)
