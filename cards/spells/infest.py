from cards.base import Card

class Infest(Card):
    def __init__(self):
        super().__init__("Infest", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        # On frappe tout le monde sur la grille
        for target in list(battlefield.grid.values()):
            if target and hasattr(target, 'temp_toughness'):
                # On applique le malus temporaire
                target.temp_power -= 2
                target.temp_toughness -= 2
                    
        return "Infest: -2/-2 until end of turn"