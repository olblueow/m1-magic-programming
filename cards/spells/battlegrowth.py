from cards.base import Card

class Battlegrowth(Card):
    def __init__(self):
        super().__init__("Battlegrowth", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        index = int(annotation) 
        
        battlefield.memory[index].counters += 1
        battlefield.memory[index].power += 1
        battlefield.memory[index].toughness += 1
        
        return f"Battlegrowth: +1/+1 (Bouclier) sur l'Index {index}"