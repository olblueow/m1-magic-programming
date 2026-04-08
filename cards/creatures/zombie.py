from cards.base import Creature

class Zombie(Creature):
    def __init__(self):
        # Un Zombie est une Créature 2/2
        super().__init__("Zombie", 2, 2)