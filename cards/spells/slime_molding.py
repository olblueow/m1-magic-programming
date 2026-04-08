from cards.base import Card
import cards.factory as factory

class SlimeMolding(Card):
    def __init__(self):
        super().__init__("Slime Molding", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        new_ooze = factory.create("Ooze")
        
        # Read the targeted coordinates (e.g., "0,5")
        row, col = map(int, annotation.split(","))
        
        # Use the battlefield's new placement function
        battlefield.place_card(new_ooze, row, col)
        
        return f"Slime Molding: +1 Ooze placed at [{row}, {col}]"