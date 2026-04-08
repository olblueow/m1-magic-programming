from cards.base import Card

class RotlungReanimator(Card):
    def __init__(self):
        super().__init__("Rotlung Reanimator", "Permanent")
        self.watch_type = None
        self.create_type = None
        self.configured = False

    def execute(self, battlefield, annotation="") -> str:
        battlefield.processor.append(self)
        return "Rotlung Reanimator enters the battlefield"

    def trigger(self, died_type: str, battlefield, index: int) -> str | None:
        # On vérifie explicitement que create_type n'est pas "None" pour rassurer Pylance
        if not self.configured or self.create_type is None or died_type != self.watch_type:
            return None

        import cards.factory as factory
        
        # Pylance sait maintenant de façon certaine que self.create_type est un texte
        nouveau_jeton = factory.create(self.create_type)
        battlefield.memory[index] = nouveau_jeton
        
        return f"Rotlung Trigger: {died_type} mort ➔ {self.create_type} créé (Index {index})"