import os
import sys
import requests
import jsonpickle
import time
from datetime import datetime

from requests.models import codes

last_setcode = ""

UPDATE_FILE = "last_update.json"
SCRYFALL_SETS_SEARCH_URL = "https://api.scryfall.com/sets?order%3Dreleased"
ILLEGAL_SET_TYPES = ["token", "memorabilia", "funny"]

# given a date, fetches list of all sets released after


def fetch_set_codes(last_setcode):
    print("hit fetch set codes")
    total_sets = []
    sets_to_load = []
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
    for card_set in total_sets:
        release_date = datetime.strptime(card_set["released_at"], '%Y-%m-%d')
        if card_set["code"] == last_setcode:
            break
        if release_date < today:
            if card_set["set_type"] not in ILLEGAL_SET_TYPES:
                sets_to_load.append(card_set["code"])

    return sets_to_load


# ---------------------------------------------------------
if os.path.exists(UPDATE_FILE):
    with open(UPDATE_FILE) as time_file:
        data = jsonpickle.decode(time_file.read())
        last_setcode = data["last_setcode"]

print("previous date found, commencing fetch of set codes")
codes_to_update = fetch_set_codes(last_setcode)
print(codes_to_update)
# insert logic calling add_set or whatever we decide
# update stored date with current time
update_data = {}
update_data["last_update"] = datetime.now().strftime('%Y-%m-%d')
update_data["last_setcode"] = codes_to_update[0]

with open(UPDATE_FILE, 'w') as output_file:
    full_json_text = jsonpickle.encode(
        value=update_data, indent=2, separators=(",", ": "))
    output_file.write(full_json_text)
