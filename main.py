from loader import DeckLoader
from battlefield import Battlefield
from engine import GameEngine
import cards.factory as factory
from time import sleep

def main():
    # 1. Charger le deck compilé
    loader = DeckLoader("data/python_compiled.cod")
    
    # 2. Initialiser le plateau de jeu (grille 2D creuse)
    board = Battlefield()
    
    # 3. Lancer le moteur de jeu (l'arbitre)
    game = GameEngine(board)
    
    for step, inst in enumerate(loader.instructions, 1):
        card = factory.create(inst["card"])
        if not card:
            print("Carte introuvable :", inst["card"])
            continue

        # Le moteur résout la carte sur le plateau
        log = game.resolve(card, inst["annotation"])
        
        if card.type != "Token": 
            print(f"[{step:03d}] {card.name} -> {log}")
        
        # Observer la ligne 0 (Mémoire) et la ligne 1 (CPU) dynamiquement
        for i in [0, 1]:
            active_cols_in_row = sorted([coords[1] for coords in board.grid.keys() if coords[0] == i])
            
            if not active_cols_in_row:
                continue
                
            row_display = []
            for c in active_cols_in_row:
                card_obj = board.get_card_at(i, c)
                
                if card_obj is not None:
                    if hasattr(card_obj, 'power'):
                        row_display.append(f"[{c}]: {card_obj.name} ({card_obj.power}/{card_obj.toughness})")
                    else:
                        row_display.append(f"[{c}]: {card_obj.name}")
                    
            print(f"Row {i} -> {', '.join(row_display)}")
            
        sleep(0.1)

    # --- LECTURE ET DÉCODAGE DE LA BANDE (MÉMOIRE) ---
    print("\n" + "="*40)
    print("ÉTAT FINAL DE LA MÉMOIRE")
    print("="*40)
    
    bits = []
    row_0_cols = sorted([coords[1] for coords in board.grid.keys() if coords[0] == 0])
    
    # Lire la bande de gauche à droite
    for col in row_0_cols:
        creature = board.get_card_at(0, col)
        if creature is not None:
            if creature.name == "Zombie":
                bits.append("1")
            elif creature.name == "Ooze":
                bits.append("0")
    
    # Regrouper les bits par blocs de 4 (Taille d'une variable dans notre architecture)
    chunk_size = 4
    variables = [bits[i:i + chunk_size] for i in range(0, len(bits), chunk_size)]
    
    # Affichage clair des variables (On suppose que la première est x, la deuxième y, etc.)
    var_names = ["x", "y", "z", "w"] # Noms par défaut pour l'affichage
    
    for idx, var_bits in enumerate(variables):
        binary_str = "".join(var_bits)
        # Convertir la chaîne binaire en entier décimal
        decimal_val = int(binary_str, 2)
        
        name = var_names[idx] if idx < len(var_names) else f"Var_{idx}"
        print(f"Variable '{name}' : {binary_str} (Décimal : {decimal_val})")

if __name__ == "__main__":
    main()