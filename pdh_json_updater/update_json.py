"""JSON database updating functions"""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

from pdh_json_updater.scryfall_fetcher import ScryfallFetcher
from pdh_json_updater.file_handler import FileHandler
from pdh_json_updater.add_set import update_json_with_set

SCRYFALL_SETS_SEARCH_URL = "https://api.scryfall.com/sets?order%3Dreleased"
ILLEGAL_SET_TYPES = ["alchemy", "token", "memorabilia", "funny"]


class SetcodeFetchResult:  # pylint: disable=too-few-public-methods
    """Data class for card setcode results from Scryfall"""

    def __init__(self, setcodes: List[str], last_set_release_date: datetime):
        self.setcodes = setcodes
        self.last_set_release_date = last_set_release_date


def fetch_setcodes_as_recent_as(
    earliest_allowed_date: Optional[datetime],
) -> SetcodeFetchResult:
    """Given a datetime, returns a list of all codes of sets, which fulfill all conditions:

    * are already released when this check is performed
    * were released after or at the same day as the given datetime (if date is None, this condition is ignored);
    * aren't of an illegal type (such as un-sets)
    In addition to that, the release date of the newest returned set is returned as well.
    If no sets are returned, returns the given date instead."""
    print("Starting to fetch missing sets...", end=" ")
    setcodes_to_load: List[str] = []
    now = datetime.now(
        timezone.utc
    )  # We specify whatever time zone to make it time-zone-aware.

    scryfall_response = ScryfallFetcher.fetch_data(
        SCRYFALL_SETS_SEARCH_URL, raise_exceptions=True
    )
    total_sets: List[Dict[str, str]] = scryfall_response.data

    scryfall_date_format = "%Y-%m-%d"
    scryfall_release_date_timezone = timezone(
        timedelta(hours=-8)
    )  # Scryfall uses UTC -8 for release dates.

    last_set_release_date: Optional[datetime] = None
    for card_set in total_sets:
        release_date = datetime.strptime(
            card_set["released_at"], scryfall_date_format
        ).replace(
            tzinfo=scryfall_release_date_timezone
        )  # We add info about time zone.
        if (
            release_date <= now
            and (earliest_allowed_date is None or earliest_allowed_date <= release_date)
            and card_set["set_type"] not in ILLEGAL_SET_TYPES
        ):
            setcodes_to_load.append(card_set["code"])
            if last_set_release_date is None:
                # Sets are sorted by release date, so the first set we append
                # will have the most recent release date (or tied), so we save this date.
                last_set_release_date = release_date

    if last_set_release_date is None:
        last_set_release_date = earliest_allowed_date

    print(f"Done.\n" f"Fetched sets: {setcodes_to_load}")
    return SetcodeFetchResult(
        setcodes=setcodes_to_load, last_set_release_date=last_set_release_date
    )


# ---------------------------------------------------------
def main():
    """Primary entrypoint to update-json script"""
    existing_json = FileHandler.get_existing_json()
    current_last_set_release_date = FileHandler.get_last_set_release_date()

    days_to_look_behind = 1
    setcode_fetch_result = fetch_setcodes_as_recent_as(
        current_last_set_release_date - timedelta(days=days_to_look_behind)
    )
    # For simplicity we'll say N instead of days_to_look_behind.
    # We subtract N days as a safety measure to lower the odds of issues in case Scryfall is late with adding sets.
    # Ideally instead of looking at the release date of sets we'd look at the date when sets are done adding to Scryfall,
    # but as far as I know Scryfall's API doesn't have such info.

    # A problem occurs when the following things happen in this order:
    # 1. Set A is released.
    # 2. Set B is released and added to Scryfall (in whatever order).
    # 3. We run update_json, which adds set B and saves its release date.
    # 4. Set A is added to Scryfall.
    # 5. We run update_json again, so we fetch all sets released since set B, minus N days.
    # 6. Now, if set A was released more than N days before set B, it won't be added to our JSON.
    codes_to_update = setcode_fetch_result.setcodes
    new_last_set_release_date = setcode_fetch_result.last_set_release_date

    # for each code found required to update the commander json, iterates through to add the set to the existing cards
    for code in codes_to_update:
        update_json_with_set(code, existing_json)

    FileHandler.save_format_json_to_file(
        existing_json, new_last_set_release_date
    )


main()
