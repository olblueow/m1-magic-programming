from cards.base import Card

class FateTransfer(Card):
    def __init__(self):
        super().__init__("Fate Transfer", "Spell")

    def execute(self, battlefield, annotation="") -> str:
        source_str, dest_str = annotation.split("|")
        s_row, s_col = map(int, source_str.split(","))
        d_row, d_col = map(int, dest_str.split(","))
        
        source = battlefield.grid[s_row][s_col]
        dest = battlefield.grid[d_row][d_col]
        
        if source and dest and hasattr(source, 'counters') and source.counters > 0:
            source.counters -= 1
            dest.counters += 1
            
            source.power -= 1
            source.toughness -= 1
            dest.power += 1
            dest.toughness += 1
            
            return f"Fate Transfer: Counter moved from [{s_row},{s_col}] to [{d_row},{d_col}]"
            
        return "Fate Transfer: Invalid target or no counter found on source."