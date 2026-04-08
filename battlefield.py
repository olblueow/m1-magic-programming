class Battlefield:
    def __init__(self):
        self.grid = [[], []] 
        self.graveyard = []

    def place_card(self, card, row: int, col: int):
        """Places a card at exact coordinates, expanding the grid if necessary."""
        # Safety: add rows if the requested row doesn't exist
        while len(self.grid) <= row:
            self.grid.append([])
            
        # Safety: add "holes" (None) if the column doesn't exist yet
        while len(self.grid[row]) <= col:
            self.grid[row].append(None)
            
        # Finally, place the card at its exact memory address!
        self.grid[row][col] = card