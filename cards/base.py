class Card:
    def __init__(self, name: str, card_type: str):
        self.name = name
        self.type = card_type
        
    def execute(self, battlefield, annotation: str = "") -> str:
        return ""

class Creature(Card):
    def __init__(self, name: str, power: int, toughness: int):
        super().__init__(name, "Creature")
        self.power = power
        self.toughness = toughness
        self.counters = 0