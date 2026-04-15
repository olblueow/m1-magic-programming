from cards.base import Creature

class Cleric(Creature):
    def __init__(self):
        # Un Cleric de base, Créature 2/2 sans aucun effet spécial
        super().__init__("Cleric", 2, 2)