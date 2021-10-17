from datetime import datetime
from typing import List, Dict, Optional

from scryfall_fetcher import ScryfallFetcher
from file_handler import FileHandler
from add_set import update_json_with_set

SCRYFALL_SETS_SEARCH_URL = "https://api.scryfall.com/sets?order%3Dreleased"
ILLEGAL_SET_TYPES = ["token", "memorabilia", "funny"]

class SetcodeFetchResult:
    def __init__(self, setcodes: List[str], last_set_release_date: datetime):
        self.setcodes = setcodes
        self.last_set_release_date = last_set_release_date


def fetch_setcodes_as_recent_as(date: Optional[datetime]) -> SetcodeFetchResult:
    """Given a datetime, returns a list of all codes of sets, which fulfill all conditions:

    * were released yesterday or earlier;
    * were released after or at the same day as the given datetime (if date is None, this condition is ignored);
    * aren't of an illegal type (such as un-sets)
    In addition to that, the release date of the newest returned set is returned as well.
    If no sets are returned, returns the given date instead."""
    print("Starting to fetch missing sets...", end=' ')
    setcodes_to_load: List[str] = []
    today = datetime.now()

    scryfall_response = ScryfallFetcher.fetch_data(SCRYFALL_SETS_SEARCH_URL, raise_exceptions=True)
    total_sets: List[Dict[str, str]] = scryfall_response.data

    # The first card_set is the most recent one.
    last_set_release_date: Optional[datetime] = None
    for card_set in total_sets:
        release_date = datetime.strptime(card_set["released_at"], '%Y-%m-%d')
        # We are using '%Y-%m-%d' instead of the DATE_FORMAT constant
        # because how Scryfall stores dates doesn't have to match how we store dates.
        if release_date < today \
                and (date is None or date <= release_date) \
                and card_set["set_type"] not in ILLEGAL_SET_TYPES:
            setcodes_to_load.append(card_set["code"])
            if last_set_release_date is None:
                # Sets are sorted by release date, so the first set we append
                # will have the most recent release date (or tied), so we save this date.
                last_set_release_date = release_date

    if last_set_release_date is None:
        last_set_release_date = date

    print(f"Done.\n"
          f"Fetched sets: {setcodes_to_load}")
    return SetcodeFetchResult(setcodes=setcodes_to_load, last_set_release_date=last_set_release_date)


# ---------------------------------------------------------
def main():
    existing_json = FileHandler.get_existing_json()
    current_last_set_release_date = FileHandler.get_last_set_release_date()

    setcode_fetch_result = fetch_setcodes_as_recent_as(current_last_set_release_date)
    codes_to_update = setcode_fetch_result.setcodes
    new_last_set_release_date = setcode_fetch_result.last_set_release_date

    # for each code found required to update the commander json, iterates through to add the set to the existing cards
    for code in codes_to_update:
        update_json_with_set(code, existing_json)

    FileHandler.save_format_json_to_file(existing_json, new_last_set_release_date)


main()
