from cards.base import Card
import cards.factory as factory

class SlimeMolding(Card):
    def __init__(self):
        super().__init__("Slime Molding", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        # On demande à l'usine de créer un vrai Ooze
        nouvel_ooze = factory.create("Ooze")
        battlefield.memory.append(nouvel_ooze)
        return "Slime Molding: +1 Ooze"