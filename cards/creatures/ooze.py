from cards.base import Creature

class Ooze(Creature):
    def __init__(self):
        # Un Ooze est une Créature 2/2
        super().__init__("Ooze", 2, 2)