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

        # 1. Scan the entire sparse grid to find dead creatures
        # We use list() to avoid modifying the dictionary while iterating over it
        for (row, col), creature in list(self.battlefield.grid.items()):
            if creature and hasattr(creature, 'toughness') and creature.toughness <= 0:
                self.battlefield.grid.pop((row, col)) # Remove from grid
                self.battlefield.graveyard.append(creature)
                dead.append((row, col, creature))

        # 2. Processors (living on row 1) react
        for row, col, creature in dead:
            # Find all processors currently on row 1 by filtering dictionary keys
            processors = [c for (r, c_idx), c in self.battlefield.grid.items() if r == 1]
            for proc in processors:
                proc.trigger(creature.name, self.battlefield, row, col)