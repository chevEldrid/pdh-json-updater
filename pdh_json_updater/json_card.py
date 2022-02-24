from pdh_json_updater.legality import Legality

# transforms a scryfall card object into a json card object


class JsonCard:
    PDH_BANLIST = ["Rhystic Study", "Mystic Remora",
                   "Stone-Throwing Devils", "Pradesh Gypsies", "Tempest Efreet"]
    # Cards "banned" as a workaround, e.g. due to incorrect rarities in Scryfall
    SOFT_BANLIST = ["Spatial Contortion", "Circle of Flame", "Swords to Plowshares"]
    ILLEGAL_CARD_TYPES = ["Conspiracy"]

    def __init__(self, scryfall_queried_card):
        self.scryfallOracleId: str = scryfall_queried_card["oracle_id"]
        self.name: str = scryfall_queried_card["name"]
        self.legality = JsonCard.is_legal(scryfall_queried_card)

    # determines legality of a card based on rarity (legal, legal as commander, not legal) and banlist
    @classmethod
    def is_legal(cls, scryfall_queried_card):
        front_card_face_typeline = scryfall_queried_card["type_line"].split("//")[0]
        # check for bannings
        if scryfall_queried_card["name"] in cls.PDH_BANLIST:
            return Legality.BANNED
        # fixes rarity issues by allowing certain cards to be rendered "not legal"
        if scryfall_queried_card["name"] in cls.SOFT_BANLIST:
            return Legality.NOT_LEGAL
        # check illegal card types
        if front_card_face_typeline in cls.ILLEGAL_CARD_TYPES:
            return Legality.NOT_LEGAL
        # check rarity
        if scryfall_queried_card["rarity"] == "common":
            return Legality.LEGAL
        elif scryfall_queried_card["rarity"] == "uncommon" and "Creature" in front_card_face_typeline:
            if "Land" in front_card_face_typeline:
                return Legality.NOT_LEGAL
            return Legality.LEGAL_AS_COMMANDER
        else:
            return Legality.NOT_LEGAL
