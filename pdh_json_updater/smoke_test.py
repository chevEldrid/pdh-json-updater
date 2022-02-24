from typing import Dict, List

from pdh_json_updater.file_handler import FileHandler
from pdh_json_updater.legality import Legality
from pdh_json_updater.json_card import JsonCard


class TestCard:
    def __init__(self, name, legality):
        self.name: str = name
        self.legality: str = legality


TEST_CARDS: List[TestCard] = [
    TestCard(  # Common
        name="+2 Mace",
        legality=Legality.LEGAL),
    TestCard(  # Uncommon creature
        name="Battle Cry Goblin",
        legality=Legality.LEGAL_AS_COMMANDER),
    TestCard(  # Rare
        name="Ranger Class",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Mythic rare
        name="Demilich",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Banned
        name="Rhystic Study",
        legality=Legality.BANNED),
    TestCard(  # Banned
        name="Mystic Remora",
        legality=Legality.BANNED),
    TestCard(  # Banned
        name="Stone-Throwing Devils",
        legality=Legality.BANNED),
    TestCard(  # Banned
        name="Pradesh Gypsies",
        legality=Legality.BANNED),
    TestCard(  # Banned because of ante
        name="Tempest Efreet",
        legality=Legality.BANNED),
    TestCard(  # Land
        name="Dryad Arbor",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Counter-balance to Dryad Arbor to make sure we aren't too restrictive
        name="Akoum Warrior // Akoum Teeth",
        legality=Legality.LEGAL_AS_COMMANDER),
    TestCard(  # Isn't a creature on front face
        name="Autumnal Gloom // Ancient of the Equinox",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Counter-balance to Autumnal Gloom to make sure we aren't too restrictive
        name="Soul Seizer // Ghastly Haunting",
        legality=Legality.LEGAL_AS_COMMANDER),
    TestCard(  # Digital-only
        name="Shrine Keeper",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Only physical printing is over-sized
        name="Aswan Jaguar",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Used to be legal as MTGO Promo
        name="Spatial Contortion",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Used to be legal as MTGO Promo
        name="Circle of Flame",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Used to be legal as MTGO Promo
        name="Hada Freeblade",
        legality=Legality.LEGAL_AS_COMMANDER),
    TestCard(  # Plane
        name="Akoum",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Scheme
        name="Know Evil",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Conspiracy
        name="Adriana's Valor",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Contraption
        name="Boomflinger",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Silver-bordered
        name="AWOL",
        legality=Legality.NOT_LEGAL),
    TestCard(  # Legal despite being banned in Vintage
        name="Brainstorm",
        legality=Legality.LEGAL),
    TestCard(  # Uncommon -> Common -> Rare)
        name="Fire // Ice",
        legality=Legality.LEGAL),
    TestCard(  # Legal in 99 despite being a commander
        name="Slippery Bogle",
        legality=Legality.LEGAL),
    TestCard(  # Legal only because of an MTGA printing
        name="Waterkin Shaman",
        legality=Legality.LEGAL),
    TestCard(  # Legal only because of an MTGO printing
        name="Chainer's Edict",
        legality=Legality.LEGAL),
    TestCard(  # Legal only because of Renaissance
        name="Ball Lightning",
        legality=Legality.LEGAL_AS_COMMANDER),
    TestCard(  # Legal only because of Renaissance
        name="Cursed Rack",
        legality=Legality.LEGAL),
    TestCard(  # Illegal because it cannot be included in a deck
        name="Swords to Plowshares",
        legality=Legality.NOT_LEGAL),
]


def main():
    existing_commander_json: Dict[str, JsonCard] = FileHandler.get_existing_json()
    total_tests = len(TEST_CARDS)
    total_tests_passed = 0

    for card in TEST_CARDS:
        if card.name in existing_commander_json:
            if card.legality == existing_commander_json[card.name].legality:
                total_tests_passed += 1
            else:
                print(f"TEST FAILED: Expected {card.name} to be {card.legality}, but it was {existing_commander_json[card.name].legality}.")
        elif card.legality == Legality.NOT_LEGAL:
            total_tests_passed += 1
        else:
            print(f"TEST FAILED: Expected {card.name} to be {card.legality}, but it was {Legality.NOT_LEGAL}.")

    print(f"Total Score: {total_tests_passed}/{total_tests}")


if __name__ == "__main__":
    main()
