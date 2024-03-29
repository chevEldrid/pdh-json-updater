"""Test basic database card serialization functionality"""
from typing import Dict, List

from pdh_json_updater.file_handler import FileHandler
from pdh_json_updater.legality import Legality
from pdh_json_updater.json_card import JsonCard


class MockCard:  # pylint: disable=too-few-public-methods
    """Mock dataclass for cards stored in JSON database"""

    def __init__(self, name, legality):
        self.name: str = name
        self.legality: str = legality


TEST_CARDS: List[MockCard] = [
    MockCard(name="+2 Mace", legality=Legality.LEGAL),  # Common
    MockCard(  # Uncommon creature
        name="Battle Cry Goblin", legality=Legality.LEGAL_AS_COMMANDER
    ),
    MockCard(name="Ranger Class", legality=Legality.NOT_LEGAL),  # Rare
    MockCard(name="Demilich", legality=Legality.NOT_LEGAL),  # Mythic rare
    MockCard(name="Rhystic Study", legality=Legality.BANNED),  # Banned
    MockCard(name="Mystic Remora", legality=Legality.BANNED),  # Banned
    MockCard(name="Stone-Throwing Devils", legality=Legality.BANNED),  # Banned
    MockCard(name="Pradesh Gypsies", legality=Legality.BANNED),  # Banned
    MockCard(name="Tempest Efreet", legality=Legality.BANNED),  # Banned because of ante
    MockCard(name="Dryad Arbor", legality=Legality.NOT_LEGAL),  # Land
    MockCard(  # Counter-balance to Dryad Arbor to make sure we aren't too restrictive
        name="Akoum Warrior // Akoum Teeth", legality=Legality.LEGAL_AS_COMMANDER
    ),
    MockCard(  # Isn't a creature on front face
        name="Autumnal Gloom // Ancient of the Equinox", legality=Legality.NOT_LEGAL
    ),
    MockCard(  # Counter-balance to Autumnal Gloom to make sure we aren't too restrictive
        name="Soul Seizer // Ghastly Haunting", legality=Legality.LEGAL_AS_COMMANDER
    ),
    MockCard(name="Shrine Keeper", legality=Legality.NOT_LEGAL),  # Digital-only
    MockCard(  # Only physical printing is over-sized
        name="Aswan Jaguar", legality=Legality.NOT_LEGAL
    ),
    MockCard(  # Used to be legal as MTGO Promo
        name="Spatial Contortion", legality=Legality.NOT_LEGAL
    ),
    MockCard(  # Used to be legal as MTGO Promo
        name="Circle of Flame", legality=Legality.NOT_LEGAL
    ),
    MockCard(  # Used to be legal as MTGO Promo
        name="Hada Freeblade", legality=Legality.LEGAL_AS_COMMANDER
    ),
    MockCard(name="Akoum", legality=Legality.NOT_LEGAL),  # Plane
    MockCard(name="Know Evil", legality=Legality.NOT_LEGAL),  # Scheme
    MockCard(name="Adriana's Valor", legality=Legality.NOT_LEGAL),  # Conspiracy
    MockCard(name="Boomflinger", legality=Legality.NOT_LEGAL),  # Contraption
    MockCard(name="AWOL", legality=Legality.NOT_LEGAL),  # Silver-bordered
    MockCard(  # Legal despite being banned in Vintage
        name="Brainstorm", legality=Legality.LEGAL
    ),
    MockCard(  # Uncommon -> Common -> Rare)
        name="Fire // Ice", legality=Legality.LEGAL
    ),
    MockCard(  # Legal in 99 despite being a commander
        name="Slippery Bogle", legality=Legality.LEGAL
    ),
    MockCard(  # Legal only because of an MTGO printing
        name="Chainer's Edict", legality=Legality.LEGAL
    ),
    MockCard(  # Legal only because of Renaissance
        name="Ball Lightning", legality=Legality.LEGAL_AS_COMMANDER
    ),
    MockCard(  # Legal only because of Renaissance
        name="Cursed Rack", legality=Legality.LEGAL
    ),
    MockCard(  # Illegal because it cannot be included in a deck
        name="Swords to Plowshares", legality=Legality.NOT_LEGAL
    ),
    MockCard ( # Legal As Commander Uncommon Background
        name="Acolyte of Bahamut", legality=Legality.LEGAL_AS_COMMANDER
    ),
    MockCard ( # Legal in 99 Common Background
        name="Candlekeep Sage", legality=Legality.LEGAL
    ),
    MockCard( # Legal As Commander from Unset
        name="Ambassador Blorpityblorpboop", legality=Legality.LEGAL_AS_COMMANDER
    ),
    MockCard( # Illegal Commander from Unset
        name="Juggletron", legality=Legality.NOT_LEGAL
    ),
    MockCard( # Legal in 99 from Unset
        name="Croakid Amphibonaut", legality=Legality.LEGAL
    ),
    MockCard( # Illegal in 99 from Unset
        name="Bar Entry", legality=Legality.NOT_LEGAL
    ),
    MockCard( # Legal card type (Attraction)
        name="Clown Extruder", legality=Legality.LEGAL
    ),
    MockCard( # Illegal due to Arena-specific downshift
        name="Spiritual Guardian", legality=Legality.NOT_LEGAL
    )
]


def test_smoke():
    """Test basic database operations"""
    existing_commander_json: Dict[str, JsonCard] = FileHandler.get_existing_json()
    total_tests = len(TEST_CARDS)
    total_tests_passed = 0

    for card in TEST_CARDS:
        if card.name in existing_commander_json:
            if card.legality.value == existing_commander_json[card.name].legality:
                total_tests_passed += 1
            else:
                print(
                    f"TEST FAILED: Expected {card.name} to be {card.legality}, but it was {existing_commander_json[card.name].legality}."
                )
        elif card.legality == Legality.NOT_LEGAL:
            total_tests_passed += 1
        else:
            print(
                f"TEST FAILED: Expected {card.name} to be {card.legality}, but it was {Legality.NOT_LEGAL}."
            )

    assert total_tests_passed == total_tests
