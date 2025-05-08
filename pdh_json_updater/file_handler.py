"""File handlers classes"""

from datetime import datetime, timezone
import os
import json
from typing import List, Dict, Optional

from pdh_json_updater.json_card import JsonCard


class FileHandler:
    """File handler abstraction for stored json data"""

    RESULT_FILE = "pauper_commander.json"
    UPDATE_METADATA_FILE = "last_update_metadata.json"
    DATE_FORMAT = "%Y-%m-%d%z"

    @classmethod
    def get_existing_json(cls) -> Dict[str, JsonCard]:
        """Gets the JSON file storing legality information about all cards and returns a Dict[str, JsonCard].
        If the file doesn't exist, an empty dict is returned."""
        existing_json: Dict[str, JsonCard] = {}
        if os.path.exists(cls.RESULT_FILE):
            with open(cls.RESULT_FILE, encoding="utf-8") as card_file:
                data: List[Dict] = json.load(card_file)
                for card_data in data:
                    card = JsonCard.__new__(JsonCard)
                    card.scryfallOracleId = card_data["scryfallOracleId"]
                    card.name = card_data["name"]
                    card.legality = card_data["legality"]
                    card.isPauperCommander = card_data["isPauperCommander"]
                    existing_json[card.scryfallOracleId] = card
        return existing_json

    @classmethod
    def get_existing_json_names(cls) -> Dict[str, JsonCard]:
        """Gets the JSON file storing legality information about all cards and returns a Dict[str, JsonCard].
        If the file doesn't exist, an empty dict is returned. This particular one sorts by name for test ease
        """
        existing_json: Dict[str, JsonCard] = {}
        if os.path.exists(cls.RESULT_FILE):
            with open(cls.RESULT_FILE, encoding="utf-8") as card_file:
                data: List[Dict] = json.load(card_file)
                for card_data in data:
                    card = JsonCard.__new__(JsonCard)
                    card.scryfallOracleId = card_data["scryfallOracleId"]
                    card.name = card_data["name"]
                    card.legality = card_data["legality"]
                    card.isPauperCommander = card_data["isPauperCommander"]
                    existing_json[card.name] = card
        return existing_json

    @classmethod
    def get_last_set_release_date(cls) -> Optional[datetime]:
        """Gets the JSON file storing update metadata and returns the last set's release date as a time-zone-aware datetime.
        If the file doesn't exist, None is returned."""
        if os.path.exists(cls.UPDATE_METADATA_FILE):
            with open(
                cls.UPDATE_METADATA_FILE, encoding="utf-8"
            ) as update_metadata_file:
                data: Dict[str, str] = json.load(update_metadata_file)
                string_last_set_release_date = data["last_set_release_date"]
                try:
                    last_set_release_date = datetime.strptime(
                        string_last_set_release_date, cls.DATE_FORMAT
                    )
                except ValueError:
                    # Backwards compatibility: If there is no time zone info in the stored date, we assume it's in UTC 0.
                    last_set_release_date = datetime.strptime(
                        string_last_set_release_date, "%Y-%m-%d"
                    ).replace(tzinfo=timezone.utc)
                return last_set_release_date
        else:
            return None

    @classmethod
    def save_format_json_to_file(
        cls,
        updated_format_json: Dict[str, JsonCard],
        last_set_release_date: Optional[datetime] = None,
    ):
        """Given a Dict[str, JsonCard], saves it to the main file.
        If last_set_release_date isn't None, it's saved to the update metadata file."""
        format_list = list(updated_format_json.values())
        format_list.sort(key=lambda x: x.name, reverse=False)

        with open(cls.RESULT_FILE, "w", encoding="utf-8") as output_file:
            json.dump(
                [card.to_json() for card in format_list],
                output_file,
                indent=2,
                sort_keys=True
            )
            print(f"JSON successfully saved to {cls.RESULT_FILE}.")

        if last_set_release_date is not None:
            update_metadata = {
                "last_set_release_date": last_set_release_date.strftime(cls.DATE_FORMAT)
            }

            with open(cls.UPDATE_METADATA_FILE, "w", encoding="utf-8") as output_file:
                json.dump(update_metadata, output_file, indent=2, sort_keys=True)
            print(
                f"Last set's release date successfully saved to {cls.UPDATE_METADATA_FILE}."
            )
