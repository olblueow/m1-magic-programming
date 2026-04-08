from cards.base import Card

class Infest(Card):
    def __init__(self):
        super().__init__("Infest", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        for creature in battlefield.memory:
            if creature:
                creature.toughness -= 2
                creature.power -= 2
                
        return "Infest: -2/-2 global"