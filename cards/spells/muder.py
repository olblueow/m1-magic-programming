from cards.base import Card

class Murder(Card):
    def __init__(self):
        super().__init__("Murder", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        # Target: "row,col" (Kills the creature at exact coordinates)
        row, col = map(int, annotation.split(","))
        
        # CHANGEMENT : Utilisation de get_card_at
        target = battlefield.get_card_at(row, col)
        
        if target:
            # Set toughness to 0 so the Game Engine triggers its death
            target.toughness = 0
            return f"Murder: Target at [{row}, {col}] was assassinated."
            
        return f"Murder: No target found at [{row}, {col}]."