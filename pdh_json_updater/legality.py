"""Card legality enumeration"""

from enum import Enum


class Legality(Enum):
    """Enumerates possible card legalities in the PDH format"""

    BANNED = "Banned"
    LEGAL = "Legal"
    NOT_LEGAL = "Not Legal"
