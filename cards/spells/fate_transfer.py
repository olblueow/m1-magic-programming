from cards.base import Card

class FateTransfer(Card):
    def __init__(self):
        super().__init__("Fate Transfer", "Spell")

    def execute(self, battlefield, annotation=""):
        idx = [i for i, c in enumerate(battlefield.memory) if c and c.counters == 0][0]
        
        battlefield.memory[idx-1].counters -= 1
        battlefield.memory[idx].counters += 1
        
        return f"Fate Transfer: Déplacement à gauche (Index {idx-1})"