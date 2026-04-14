class Card:
    def __init__(self, name: str, card_type: str):
        self.name = name
        self.type = card_type
        
    def execute(self, battlefield, annotation: str = "") -> str:
        return ""

class Creature(Card):
    def __init__(self, name: str, power: int, toughness: int):
        super().__init__(name, "Creature")
        # --- Statistiques permanentes ---
        self.base_power = power
        self.base_toughness = toughness
        
        # --- Modificateurs temporaires ("jusqu'à la fin du tour") ---
        self.temp_power = 0
        self.temp_toughness = 0
        
        self.counters = 0

    @property
    def power(self):
        """Calcule la force réelle en additionnant la base et le modificateur."""
        return self.base_power + self.temp_power

    @property
    def toughness(self):
        """Calcule l'endurance réelle en additionnant la base et le modificateur."""
        return self.base_toughness + self.temp_toughness

    def cleanup_end_of_turn(self):
        """La Cleanup Step ! Remet les modificateurs à zéro."""
        self.temp_power = 0
        self.temp_toughness = 0