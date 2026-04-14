from loader import DeckLoader
from battlefield import Battlefield
from engine import GameEngine
import cards.factory as factory
from time import sleep

def main():
    # 1. Load the deck
    loader = DeckLoader("data/physics_test.cod")
    
    # 2. Setup the empty battlefield with its sparse 2D grid
    board = Battlefield()
    
    # 3. Call the engine (referee) and show it the board
    game = GameEngine(board)
    
    for step, inst in enumerate(loader.instructions, 1):
        card = factory.create(inst["card"])
        if not card:
            print("Card not found:", inst["card"])
            continue

        # The engine resolves the card on the board!
        log = game.resolve(card, inst["annotation"])
        
        if card.type != "Token": 
            print(f"[{step:03d}] {card.name} -> {log}")
        
        # Observe row 0 and row 1 dynamically (Sparse Mode)
        for i in [0, 1]:
            # Find all columns currently occupied in this specific row, sorted from lowest to highest
            active_cols_in_row = sorted([coords[1] for coords in board.grid.keys() if coords[0] == i])
            
            # If the row is completely empty, skip printing it entirely
            if not active_cols_in_row:
                continue
                
            row_display = []
            for c in active_cols_in_row:
                card_obj = board.get_card_at(i, c)
                
                # 👉 AJOUT ICI : On vérifie que card_obj existe bien pour Pylance
                if card_obj is not None:
                    if hasattr(card_obj, 'power'):
                        row_display.append(f"[{c}]: {card_obj.name} ({card_obj.power}/{card_obj.toughness})")
                    else:
                        row_display.append(f"[{c}]: {card_obj.name}")
                    
            # Print nicely formatted
            print(f"Row {i} -> {', '.join(row_display)}")
            
        sleep(0.1)  # Pause to better visualize the animation

    # Translate row 0 to binary
    bits = []
    # Find the active columns specifically on row 0, sorted lowest to highest (including negatives!)
    row_0_cols = sorted([coords[1] for coords in board.grid.keys() if coords[0] == 0])
    
    # Read the tape from lowest index to highest
    for col in row_0_cols:
        creature = board.get_card_at(0, col)
        
        # 👉 AJOUT ICI : On vérifie que creature existe bien pour Pylance
        if creature is not None:
            if creature.name == "Zombie":
                bits.append(1)
            elif creature.name == "Ooze":
                bits.append(0)
    
    binary_str = "".join(str(b) for b in bits)

    print(f"\nResult (Binary) : {binary_str}")

if __name__ == "__main__":
    main()