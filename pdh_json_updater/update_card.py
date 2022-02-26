"""Database updater script for a single card entry"""
import logging
from argparse import ArgumentParser
from argparse import Namespace
from typing import Dict

from pdh_json_updater.file_handler import FileHandler
from pdh_json_updater.legality import Legality
from pdh_json_updater.json_card import JsonCard

LOGGER = logging.getLogger(__name__)


def parse_update_card() -> Namespace:
    """Parse cli options for the `update-card` script"""
    parser = ArgumentParser(description="Update the legality entry for a card")
    parser.add_argument("card_name", help="Oracle name of the card to be updated")
    parser.add_argument(
        "legality",
        help="Legality to assign to the given card",
        choices=[leg.name for leg in Legality],
    )
    return parser.parse_args()


def update_card_in_json(
    card_name: str, updated_legality: str, existing_format_json: Dict[str, JsonCard]
):
    """Given a card name, its new legality, and a dict with legality info, updates the entry for that card in that dict."""
    if card_name in existing_format_json:
        prev_card_ruling = existing_format_json[card_name]
        try:
            prev_card_ruling.legality = Legality[updated_legality].value
            LOGGER.info("Card object updated!")
        except KeyError:
            LOGGER.warning("ERROR: illegal rarity provided")
    else:
        LOGGER.warning(f"ERROR: {card_name} not found in existing commander json.")


def main():
    """Primary entrypoint for `update-card` script"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    update_card_args = parse_update_card()
    format_json = FileHandler.get_existing_json()
    update_card_in_json(
        update_card_args.card_name, update_card_args.legality, format_json
    )
    FileHandler.save_format_json_to_file(format_json)


if __name__ == "__main__":
    main()
