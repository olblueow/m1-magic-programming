from .mapper import SymbolTable

class Translator:
    """Translates intermediate tokens into actual Magic The Gathering card actions."""
    
    def __init__(self):
        self.symbols = SymbolTable(bit_width=4)
        self.decklist = []

    def translate(self, ast_tokens: list):
        # --- PHASE 1 : BOOT SEQUENCE (HARDWARE SETUP) ---
        self.decklist.append({"card": "Rotlung Reanimator", "annotation": "1,0"})
        # 👇 NOUVEAU : On protège le processeur pour qu'il devienne 3/3 et survive à Infest !
        self.decklist.append({"card": "Battlegrowth", "annotation": "1,0"}) 
        self.decklist.append({"card": "Artificial Evolution", "annotation": "1,0|Cleric|Ooze"})

        for tokens in ast_tokens:
            cmd = tokens[0].upper()
            
            if cmd == "ALLOCATE":
                var_name = tokens[1]
                value = tokens[2]
                cols = self.symbols.allocate(var_name) 
                
                binary_str = format(value, f'0{self.symbols.bit_width}b')
                
                # --- PHASE 2 : MEMORY INITIALIZATION ---
                for i, bit in enumerate(binary_str):
                    col = cols[i]
                    
                    # 1. On crée la case mémoire "vierge" (Un Ooze 2/2)
                    self.decklist.append({"card": "Slime Molding", "annotation": f"0,{col}"})
                    
                    if bit == '1':
                        # 2. Si on veut un '1', on active l'horloge !
                        # L'Infest tue l'Ooze non protégé. 
                        # Le Rotlung Reanimator le voit et génère un Zombie 2/2 à la place.
                        self.decklist.append({"card": "Infest", "annotation": "Write '1' Cycle"})
                        
                    # 3. On protège la case finale (qu'elle soit restée Ooze ou devenue Zombie)
                    # La carte devient 3/3 et survivra aux futurs 'Infest'.
                    self.decklist.append({"card": "Battlegrowth", "annotation": f"0,{col}"})
                
            elif cmd == "ADD_COUNTER":
                # (Simulation simplifiée pour l'instant de l'incrémentation)
                var_name = tokens[1]
                cols = self.symbols.get_address_block(var_name)
                lsb_col = cols[-1] 
                self.decklist.append({"card": "Battlegrowth", "annotation": f"0,{lsb_col}"})
                self.decklist.append({"card": "Infest", "annotation": "Clock Cycle Triggered"})
                
            elif cmd == "MOVE":
                src, dest = tokens[1], tokens[2]
                src_cols = self.symbols.get_address_block(src)
                dest_cols = self.symbols.get_address_block(dest)
                for s_col, d_col in zip(src_cols, dest_cols):
                    self.decklist.append({"card": "Bioshift", "annotation": f"0,{s_col}|0,{d_col}"})
                
        return self.decklist