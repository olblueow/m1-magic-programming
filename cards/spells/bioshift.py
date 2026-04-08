from cards.base import Card
import cards.factory as factory

class Bioshift(Card):
    def __init__(self):
        super().__init__("Bioshift", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        idx = [i for i, c in enumerate(battlefield.memory) if c and c.counters == 0][0]
        
        if idx + 1 >= len(battlefield.memory):
            nouvel_ooze = factory.create("Ooze")
            if nouvel_ooze:
                nouvel_ooze.counters = 1  # type: ignore
                battlefield.memory.append(nouvel_ooze)
                
        battlefield.memory[idx+1].counters -= 1
        battlefield.memory[idx].counters += 1
        
        return f"Bioshift: Déplacement à droite (Index {idx+1})"