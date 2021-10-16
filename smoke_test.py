import os
import jsonpickle
from typing import Dict

from add_set import NOT_LEGAL, JsonCard

LEGAL_FILE = "pauper-commander.json"
UNIT_TEST_FILE = "test_suite.json"


class TestCard:
    def __init__(self, test_card):
        self.name = test_card["name"]
        self.legality = test_card["legality"]


def main():
    existing_commander_json: Dict[str, JsonCard] = {}
    cards_to_test: Dict[str, TestCard] = {}

    if os.path.exists(LEGAL_FILE):
        with open(LEGAL_FILE) as card_file:
            data = jsonpickle.decode(card_file.read())
            for card in data:
                existing_commander_json[card.name] = card

    if os.path.exists(UNIT_TEST_FILE):
        with open(UNIT_TEST_FILE) as card_file:
            data = jsonpickle.decode(card_file.read())
            for card in data:
                testCard = TestCard(card)
                cards_to_test[testCard.name] = testCard

    total_tests = len(cards_to_test)
    total_tests_passed = 0

    for card in cards_to_test.values():
        if card.name in existing_commander_json:
            if card.legality == existing_commander_json[card].legality:
                total_tests_passed = total_tests_passed + 1
            else:
                print("TEST FAILED: Expected "+card.name+" to be " +
                      card.legality+", but it was "+existing_commander_json[card].legality)
        elif card.legality == NOT_LEGAL:
            total_tests_passed = total_tests_passed + 1
        else:
            print("TEST FAILED: Expected "+card.name+" to be " +
                  card.legality+", but it was "+NOT_LEGAL)

    print("Total Score: "+str(total_tests_passed)+"/"+str(total_tests))


if __name__ == "__main__":
    main()
