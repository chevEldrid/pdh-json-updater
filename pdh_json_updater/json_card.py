"""Transforms a Scryfall card object into a json card object"""
from pdh_json_updater.legality import Legality


class JsonCard:  # pylint: disable=too-few-public-methods
    """JSON serialization class for MTG cards"""

    PDH_BANLIST = [
        "Rhystic Study",
        "Mystic Remora",
        "Stone-Throwing Devils",
        "Pradesh Gypsies",
        "Tempest Efreet",
    ]
    # Cards "banned" as a workaround, e.g. due to incorrect rarities in Scryfall
    SOFT_BANLIST = ["Spatial Contortion", "Circle of Flame", "Swords to Plowshares"]
    ILLEGAL_CARD_TYPES = ["Conspiracy"]

    def __init__(self, scryfall_queried_card):

        # some sl printings don't have oracle ids in scryfall...
        if "oracle_id" in scryfall_queried_card:
            self.scryfallOracleId: str = (  # pylint: disable=invalid-name
                scryfall_queried_card["oracle_id"]
            )
        else:
            self.scryfallOracleId: str = ""

        self.name: str = scryfall_queried_card["name"]
        self.legality = JsonCard.is_legal(scryfall_queried_card)

    # determines legality of a card based on rarity (legal, legal as commander, not legal) and banlist
    @classmethod
    def is_legal(
        cls, scryfall_queried_card
    ):  # pylint: disable=too-many-return-statements
        """Get a MTG card's PDH legality"""

        if "type_line" in scryfall_queried_card:
            front_card_face_typeline = scryfall_queried_card["type_line"].split("//")[0]
        else:
            front_card_face = scryfall_queried_card["card_faces"][0]
            front_card_face_typeline = front_card_face["type_line"]
        # check for bannings
        if scryfall_queried_card["name"] in cls.PDH_BANLIST:
            return Legality.BANNED.value
        # fixes rarity issues by allowing certain cards to be rendered "not legal"
        if scryfall_queried_card["name"] in cls.SOFT_BANLIST:
            return Legality.NOT_LEGAL.value
        # check illegal card types
        if front_card_face_typeline in cls.ILLEGAL_CARD_TYPES:
            return Legality.NOT_LEGAL.value
        # check illegal game types
        if (
            "paper" not in scryfall_queried_card["games"]
            and "mtgo" not in scryfall_queried_card["games"]
        ):
            return Legality.NOT_LEGAL.value
        # check rarity
        if scryfall_queried_card["rarity"] == "common":
            return Legality.LEGAL.value
        # check for backgrounds, Legal Enchantment Commanders
        if (
            scryfall_queried_card["rarity"] == "uncommon"
            and "Background" in front_card_face_typeline
        ):
            return Legality.LEGAL_AS_COMMANDER.value
        if (
            scryfall_queried_card["rarity"] == "uncommon"
            and "Creature" in front_card_face_typeline
        ):
            if "Land" in front_card_face_typeline:
                return Legality.NOT_LEGAL.value
            return Legality.LEGAL_AS_COMMANDER.value
        return Legality.NOT_LEGAL.value
