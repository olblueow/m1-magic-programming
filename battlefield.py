class Battlefield:
    def __init__(self):
        # Using a dictionary for a Sparse Matrix: {(row, col): card_object}
        self.grid = {} 
        self.graveyard = []

    def place_card(self, card, row: int, col: int) -> bool:
        """Places a card at exact coordinates. 
        Returns True if successful, False if occupied."""
        
        # Check for collision
        if (row, col) in self.grid:
            # Collision detected! Send the new card straight to the graveyard
            self.graveyard.append(card)
            return False
            
        # Free slot, place the card safely
        self.grid[(row, col)] = card
        return True

    def get_card_at(self, row: int, col: int):
        """Returns the card at coordinates or None if empty."""
        return self.grid.get((row, col))