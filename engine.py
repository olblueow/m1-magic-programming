class GameEngine:
    def __init__(self, battlefield):
        self.battlefield = battlefield

    def resolve(self, card, annotation=""):
        log = card.execute(self.battlefield, annotation)
        if card.type == "Spell":
            self.battlefield.graveyard.append(card)
        self.check_state_based_actions()
        return log

    def check_state_based_actions(self):
        dead = [] # Will store (row, col, creature)

        # 1. Scan the entire grid to find dead creatures
        for row_idx, row in enumerate(self.battlefield.grid):
            for col_idx, creature in enumerate(row):
                if creature and creature.toughness <= 0:
                    self.battlefield.grid[row_idx][col_idx] = None
                    self.battlefield.graveyard.append(creature)
                    dead.append((row_idx, col_idx, creature))

        # 2. Processors (living on row 1) react
        for row_idx, col_idx, creature in dead:
            for proc in self.battlefield.grid[1]:
                if proc: # If the processor is not an empty slot (died in step 1)
                    proc.trigger(creature.name, self.battlefield, row_idx, col_idx)