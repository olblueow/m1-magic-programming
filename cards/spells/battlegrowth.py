from cards.base import Card

class Battlegrowth(Card):
    def __init__(self):
        super().__init__("Battlegrowth", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        # Transforms "0,3" into row=0 and col=3
        row, col = map(int, annotation.split(",")) 
        
        target = battlefield.grid[row][col]
        if target:
            target.counters += 1
            target.power += 1
            target.toughness += 1
            
        return f"Battlegrowth: +1/+1 on target at [{row}, {col}]"