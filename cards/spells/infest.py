from cards.base import Card

class Infest(Card):
    def __init__(self):
        super().__init__("Infest", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        # Strike across all values in the dictionary
        for target in list(battlefield.grid.values()):
            if target and hasattr(target, 'toughness'):
                target.toughness -= 2
                target.power -= 2
                    
        return "Infest: -2/-2 globally across the sparse grid"