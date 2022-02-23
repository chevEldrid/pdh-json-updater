class PseudoEnum(type):
    def __contains__(cls, item):
        return item in cls.__dict__.values()


class Legality(metaclass=PseudoEnum):
    BANNED = "Banned"
    LEGAL = "Legal"
    LEGAL_AS_COMMANDER = "Legal As Commander"
    NOT_LEGAL = "Not Legal"
