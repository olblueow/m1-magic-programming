from cards.base import Creature

class Zombie(Creature):
    def __init__(self):
        super().__init__("Zombie", 2, 2)