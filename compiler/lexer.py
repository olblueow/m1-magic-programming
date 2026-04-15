import re

class Lexer:
    """Reads pure High-Level Python code and generates IR."""
    
    def tokenize(self, code_text: str):
        lines = code_text.strip().split('\n')
        instructions = []
        allocated_vars = set() # Pour savoir si on fait un ALLOCATE ou un SET
        
        for line in lines:
            clean_line = line.split('#')[0].strip()
            if not clean_line: continue
                
            # Match: x = 5 ou x = 1 * 2 par exemple
            # On verifie "var = chiffre" ou "var = chiffre operateur chiffre"
            if match := re.match(r'^([a-zA-Z_]\w*)\s*=\s*(\d+)(?:\s*([\+\-\*\/])\s*(\d+))?$', clean_line):
                var_name = match.group(1)
                val1 = int(match.group(2))
                
                # S'il y a une opération (ex: 1 * 2), le compilateur la calcule 
                if match.group(3):
                    op, val2 = match.group(3), int(match.group(4))
                    if op == '+': final_val = val1 + val2
                    elif op == '-': final_val = val1 - val2
                    elif op == '*': final_val = val1 * val2
                    elif op == '/': final_val = val1 // val2
                else:
                    final_val = val1
                    
                # Si la variable existe déjà, on l'écrase avec SET, sinon on la crée avec ALLOCATE
                if var_name in allocated_vars:
                    instructions.append(["SET", var_name, final_val])
                else:
                    instructions.append(["ALLOCATE", var_name, final_val])
                    allocated_vars.add(var_name)
                
            # Match: x += N (Incrémentation)
            elif match := re.match(r'^([a-zA-Z_]\w*)\s*\+=\s*(\d+)$', clean_line):
                for _ in range(int(match.group(2))):
                    instructions.append(["INCREMENT", match.group(1)])
                    
            # Match: y -= N (Décrémentation)
            elif match := re.match(r'^([a-zA-Z_]\w*)\s*-=\s*(\d+)$', clean_line):
                for _ in range(int(match.group(2))):
                    instructions.append(["DECREMENT", match.group(1)])

            # Match: x *= 2 (Décalage binaire gauche)
            elif match := re.match(r'^([a-zA-Z_]\w*)\s*\*\=\s*2$', clean_line):
                instructions.append(["SHIFT_LEFT", match.group(1)])
                
            else:
                raise SyntaxError(f"Compiler Error: Invalid Python syntax at line -> '{clean_line}'")
                
        return instructions