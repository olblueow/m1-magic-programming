from cards.base import Creature
import cards.factory as factory

class RotlungReanimator(Creature):
    def __init__(self):
        super().__init__("Rotlung Reanimator", 2, 2)
        # The actual default values of the printed Magic card!
        self.watch_type = "Cleric"
        self.create_type = "Zombie"

    def execute(self, battlefield, annotation="") -> str:
        # The Rotlung installs itself at the specified memory address
        row, col = map(int, annotation.split(","))
        battlefield.place_card(self, row, col)
        return f"Rotlung Reanimator installed at [{row}, {col}]"

    def trigger(self, died_type: str, battlefield, row: int, col: int) -> str | None:
        # If the creature that just died is the one we are watching...
        if died_type == self.watch_type:
            new_token = factory.create(self.create_type)
            # We resurrect it at the EXACT same coordinates!
            battlefield.grid[row][col] = new_token
            return f"Trigger: {self.create_type} created at [{row}, {col}]"
        
        return None