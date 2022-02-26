"""Card legality enumeration"""
from enum import Enum


class Legality(Enum):
    """Enumerates possible card legalities in the PDH format"""

    BANNED = "Banned"
    LEGAL = "Legal"
    LEGAL_AS_COMMANDER = "Legal As Commander"
    NOT_LEGAL = "Not Legal"
