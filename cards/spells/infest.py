from cards.base import Card

class Infest(Card):
    def __init__(self):
        super().__init__("Infest", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        # Strike across all rows and all columns
        for row in battlefield.grid:
            for target in row:
                if target and hasattr(target, 'toughness'):
                    target.toughness -= 2
                    target.power -= 2
                    
        return "Infest: -2/-2 globally across the entire grid"