from cards.base import Card

class ArtificialEvolution(Card):
    def __init__(self):
        super().__init__("Artificial Evolution", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        # Expected annotation: "1,0|Cleric|Ooze"
        coords, old_word, new_word = annotation.split("|")
        row, col = map(int, coords.split(","))
        
        # CHANGEMENT ICI : On utilise la nouvelle fonction
        target = battlefield.get_card_at(row, col)
        
        if target:
            if hasattr(target, 'watch_type') and target.watch_type == old_word:
                target.watch_type = new_word
            if hasattr(target, 'create_type') and target.create_type == old_word:
                target.create_type = new_word
                
        return f"Evolution on [{row},{col}]: '{old_word}' becomes '{new_word}'"