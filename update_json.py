import os
import requests
import jsonpickle
import time
from datetime import datetime
from typing import List, Dict, Optional

from add_set import JsonCard, fetch_set_json

RESULT_FILE = "pauper-commander.json"
UPDATE_METADATA_FILE = "last_update_metadata.json"
SCRYFALL_SETS_SEARCH_URL = "https://api.scryfall.com/sets?order%3Dreleased"
ILLEGAL_SET_TYPES = ["token", "memorabilia", "funny"]
DATE_FORMAT = '%Y-%m-%d'

class SetcodeFetchResult:
    def __init__(self, setcodes: List[str], last_set_release_date: datetime):
        self.setcodes = setcodes
        self.last_set_release_date = last_set_release_date

# Given a datetime, returns a list of all codes of sets, which fulfill all conditions:
# * were released yesterday or earlier;
# * were released after or at the same day as the given datetime;
# * aren't of an illegal type (such as un-sets)
# In addition to that, the release date of the newest returned set is returned as well.
# If no sets are returned, returns the given date instead.
def fetch_setcodes_as_recent_as(date: datetime) -> SetcodeFetchResult:
    print("hit fetch set codes")
    total_sets: List[Dict[str, str]] = []
    setcodes_to_load: List[str] = []
    today = datetime.now()
    url = SCRYFALL_SETS_SEARCH_URL
    while True:
        r = requests.get(url)
        x = jsonpickle.loads(r.text)
        total_sets.extend(x["data"])
        if x["has_more"]:
            url = x["next_page"]
            time.sleep(.15)
        else:
            break

    print("sets found, loading")

    # The first card_set is the most recent one.
    last_set_release_date: Optional[datetime] = None
    for card_set in total_sets:
        release_date = datetime.strptime(card_set["released_at"], DATE_FORMAT)
        if date <= release_date < today and card_set["set_type"] not in ILLEGAL_SET_TYPES:
            setcodes_to_load.append(card_set["code"])
            if last_set_release_date is None:
                # Sets are sorted by release date, so the first set we append
                # will have the most recent release date (or tied), so we save this date.
                last_set_release_date = release_date

    if last_set_release_date is None:
        last_set_release_date = date

    return SetcodeFetchResult(setcodes=setcodes_to_load, last_set_release_date=last_set_release_date)


# ---------------------------------------------------------
def main():
    last_set_release_date: datetime
    existing_cards: Dict[str, JsonCard] = {}
    card_list: List[JsonCard] = []

    if os.path.exists(UPDATE_METADATA_FILE):
        with open(UPDATE_METADATA_FILE) as update_metadata_file:
            data: Dict[str, str] = jsonpickle.decode(update_metadata_file.read())
            last_set_release_date = datetime.strptime(data["last_set_release_date"], DATE_FORMAT)

    if os.path.exists(RESULT_FILE):
        with open(RESULT_FILE) as card_file:
            data = jsonpickle.decode(card_file.read())
            for card in data:
                existing_cards[card.name] = card
        card_list.append(list(existing_cards.values()))

    print("previous date found, commencing fetch of set codes")
    setcode_fetch_result = fetch_setcodes_as_recent_as(last_set_release_date)
    codes_to_update = setcode_fetch_result.setcodes
    last_set_release_date = setcode_fetch_result.last_set_release_date

    print(codes_to_update)
    # for each code found required to update the commander json, iterates through to add the set to the existing cards
    for code in codes_to_update:
        new_cards: Dict[str, JsonCard]
        new_cards = fetch_set_json(code, existing_cards)
        existing_cards = {**existing_cards, **new_cards}
        card_list = card_list + list(new_cards.values())

    card_list.sort(key=lambda x: x.name, reverse=False)

    with open(RESULT_FILE, 'w') as output_file:
        full_json_text = jsonpickle.encode(
            value=card_list, indent=2, separators=(",", ": "))
        output_file.write(full_json_text)

    update_metadata = {"last_set_release_date": last_set_release_date.strftime(DATE_FORMAT)}

    with open(UPDATE_METADATA_FILE, 'w') as output_file:
        full_json_text = jsonpickle.encode(
            value=update_metadata, indent=2, separators=(",", ": "))
        output_file.write(full_json_text)


main()
