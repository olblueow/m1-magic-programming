from loader import DeckLoader
from battlefield import Battlefield
from engine import GameEngine
import cards.factory as factory
from time import sleep

def main():
    # 1. Load the deck
    loader = DeckLoader("data/test.cod")
    
    # 2. Setup the empty battlefield with its 2D grid
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
        
       # Observe row 0 and row 1 of the grid with power/toughness values
        for i in [0, 1]:
            row_display = []
            for c in board.grid[i]:
                if not c:
                    row_display.append("Empty")
                elif hasattr(c, 'power'): # Si c'est une créature
                    row_display.append(f"{c.name} ({c.power}/{c.toughness})")
                else:
                    row_display.append(c.name)
            print(f"Row {i}: {row_display}")
            
        sleep(0.1)  # Pause to better visualize the animation

    # Translate row 0 to binary
    bits = []
    for creature in board.grid[0]:
        if creature is not None:
            if creature.name == "Zombie":
                bits.append(1)
            elif creature.name == "Ooze":
                bits.append(0)
    
    binary_str = "".join(str(b) for b in bits)

    print(f"\nResult (Binary) : {binary_str}")

if __name__ == "__main__":
    main()