from cards.base import Card

class GiantGrowth(Card):
    def __init__(self):
        super().__init__("Giant Growth", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        row, col = map(int, annotation.split(","))
        
        target = battlefield.grid[row][col]
        if target:
            # Classic +3/+3 from Magic The Gathering
            target.power += 3
            target.toughness += 3
            return f"Giant Growth: +3/+3 granted to target at [{row}, {col}]"
            
        return "Giant Growth: Invalid target."