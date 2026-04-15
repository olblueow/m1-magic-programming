from .mapper import SymbolTable

class Translator:
    def __init__(self):
        self.symbols = SymbolTable(bit_width=4)
        self.decklist = []
        self.current_head = None
        self.tape_sim = {} 
        
        # Le Compilateur mémorise l'état actuel du Processeur 
        self.cpu_trigger = "Cleric"
        self.cpu_output = "Zombie"

    def _reprogram_cpu(self, target_trigger: str, target_output: str):
        """Reprogramme le CPU en utilisant 'Cleric' comme variable temporaire."""
        if self.cpu_trigger == target_trigger and self.cpu_output == target_output:
            return 

        # Cas 1 : Initialisation depuis le boot par défaut (Cleric->Zombie) vers (Ooze->Zombie)
        if self.cpu_trigger == "Cleric" and target_trigger == "Ooze" and self.cpu_output == "Zombie" and target_output == "Zombie":
            self.decklist.append({"card": "Artificial Evolution", "annotation": "1,0|Cleric|Ooze"})
            
        # Cas 2 (Le Swap) : Échange complet (ex. Ooze->Zombie vers Zombie->Ooze)
        else:
            # 1. Output actuel -> Temp (Cleric)
            self.decklist.append({"card": "Artificial Evolution", "annotation": f"1,0|{self.cpu_output}|Cleric"})
            # 2. Trigger actuel -> Nouveau Trigger
            self.decklist.append({"card": "Artificial Evolution", "annotation": f"1,0|{self.cpu_trigger}|{target_trigger}"})
            # 3. Temp (Cleric) -> Nouvel Output
            self.decklist.append({"card": "Artificial Evolution", "annotation": f"1,0|Cleric|{target_output}"})

        # Mise à jour de la mémoire du compilateur
        self.cpu_trigger = target_trigger
        self.cpu_output = target_output

    def _move_head_to(self, target_col: int):
        """Vulnérabilité 2/2 sur la bande."""
        if self.current_head is None:
            return

        while self.current_head < target_col:
            src, dest = self.current_head + 1, self.current_head
            self.decklist.append({"card": "Bioshift", "annotation": f"0,{src}|0,{dest}"})
            self.current_head += 1

        while self.current_head > target_col:
            src, dest = self.current_head - 1, self.current_head
            self.decklist.append({"card": "Fate Transfer", "annotation": f"0,{src}|0,{dest}"})
            self.current_head -= 1

    def _write_bit(self, target_bit: str):
        """Écrit un 1 ou un 0 en reprogrammant le CPU selon la case lue."""
        current_bit = self.tape_sim.get(self.current_head, '0')
        
        if current_bit == target_bit:
            return

        if current_bit == '0' and target_bit == '1':
            # Règle pour écrire un 1 : Quand l'Ooze meurt, crée un Zombie
            self._reprogram_cpu("Ooze", "Zombie")
            self.decklist.append({"card": "Infest", "annotation": f"Write '1' at [{self.current_head}]"})
            self.tape_sim[self.current_head] = '1'

        elif current_bit == '1' and target_bit == '0':
            # Règle pour écrire un 0 : Quand le Zombie meurt, crée un Ooze
            self._reprogram_cpu("Zombie", "Ooze")
            self.decklist.append({"card": "Infest", "annotation": f"Write '0' at [{self.current_head}]"})
            self.tape_sim[self.current_head] = '0'

    def translate(self, ast_tokens: list):
        # HARDWARE BOOT
        self.decklist.append({"card": "Rotlung Reanimator", "annotation": "1,0"})
        self.decklist.append({"card": "Battlegrowth", "annotation": "1,0"}) 

        for tokens in ast_tokens:
            cmd = tokens[0].upper()
            
            if cmd == "ALLOCATE":
                var_name, value = tokens[1], tokens[2]
                cols = self.symbols.allocate(var_name) 
                binary_str = format(value, f'0{self.symbols.bit_width}b')
                
                for i, bit in enumerate(binary_str):
                    col = cols[i]
                    self.decklist.append({"card": "Slime Molding", "annotation": f"0,{col}"})
                    self.tape_sim[col] = '0' 
                    
                    if self.current_head is not None:
                        self.decklist.append({"card": "Battlegrowth", "annotation": f"0,{self.current_head}"})
                    
                    self.current_head = col 
                    self._write_bit(bit)
                    
            elif cmd == "INCREMENT":
                var_name = tokens[1]
                cols = self.symbols.get_address_block(var_name)
                
                # q0 : Positionnement sur LSB
                self._move_head_to(cols[-1])
                
                # q1 : Carry Propagation
                while self.current_head >= cols[0]:
                    current_bit = self.tape_sim[self.current_head]
                    
                    if current_bit == '1':
                        self._write_bit('0')
                        self._move_head_to(self.current_head - 1)
                    else:
                        self._write_bit('1')
                        break
            
            elif cmd == "DECREMENT":
                var_name = tokens[1]
                cols = self.symbols.get_address_block(var_name)
                
                self._move_head_to(cols[-1]) # Départ sur LSB
                
                # Inverse de l'incrémentation 
                while self.current_head >= cols[0]:
                    current_bit = self.tape_sim[self.current_head]
                    
                    if current_bit == '0':
                        self._write_bit('1')
                        self._move_head_to(self.current_head - 1)
                    else:
                        self._write_bit('0')
                        break

            elif cmd == "SET":
                var_name, value = tokens[1], tokens[2]
                cols = self.symbols.get_address_block(var_name)
                binary_str = format(value, f'0{self.symbols.bit_width}b')
                
                # Le compilateur déplace la tête sur chaque case et écrit le nouveau bit
                for i, bit in enumerate(binary_str):
                    self._move_head_to(cols[i])
                    self._write_bit(bit)

            elif cmd == "SHIFT_LEFT":
                var_name = tokens[1]
                cols = self.symbols.get_address_block(var_name)
                
                # Note : En binaire, multiplier par 2 c'est décaler tous les bits vers la gauche
                # et mettre un 0 à la fin. Le compilateur calcule la nouvelle configuration :
                new_bits = [self.tape_sim.get(cols[i], '0') for i in range(1, len(cols))] + ['0']
                
                # La machine physique l'exécute :
                for i, bit in enumerate(new_bits):
                    self._move_head_to(cols[i])
                    self._write_bit(bit)

        return self.decklist