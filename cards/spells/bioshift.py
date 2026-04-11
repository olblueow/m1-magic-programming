from cards.base import Card

class Bioshift(Card):
    def __init__(self):
        super().__init__("Bioshift", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        # Expected annotation: "source_row,source_col|dest_row,dest_col"
        source_str, dest_str = annotation.split("|")
        s_row, s_col = map(int, source_str.split(","))
        d_row, d_col = map(int, dest_str.split(","))
        
        # CORRECTIF : Utilisation de get_card_at() au lieu de [][]
        source = battlefield.get_card_at(s_row, s_col)
        dest = battlefield.get_card_at(d_row, d_col)
        
        # Check if targets exist and if the source has at least one counter
        if source and dest and hasattr(source, 'counters') and source.counters > 0:
            # 1. Move the logical counter
            source.counters -= 1
            dest.counters += 1
            
            # 2. Move the PHYSICAL effect (Stats)
            source.power -= 1
            source.toughness -= 1
            dest.power += 1
            dest.toughness += 1
            
            return f"Bioshift: Counter moved from [{s_row},{s_col}] to [{d_row},{d_col}]"
            
        return "Bioshift: Invalid target or no counter found on source."