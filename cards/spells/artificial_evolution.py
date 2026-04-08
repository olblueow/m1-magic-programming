from cards.base import Card

class ArtificialEvolution(Card):
    def __init__(self):
        super().__init__("Artificial Evolution", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        parts = annotation.split("|") 
        watch = parts[0].split("=")[1]
        create = parts[1].split("=")[1]
        
        # On cible le DERNIER processeur ajouté à la bande
        rotlung = battlefield.processor[-1]
        rotlung.watch_type = watch
        rotlung.create_type = create
        rotlung.configured = True
        
        return f"Evolution: {watch} ➔ {create}"