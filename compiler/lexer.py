import re

class Lexer:
    """Reads purely logical Python-like code."""
    
    def tokenize(self, code_text: str):
        lines = code_text.strip().split('\n')
        instructions = []
        
        for line in lines:
            # 1. Remove Python comments
            clean_line = line.split('#')[0].strip()
            
            if not clean_line:
                continue
                
            # Match: x = 5 (Allocation)
            if match := re.match(r'^([a-zA-Z_]\w*)\s*=\s*(\d+)$', clean_line):
                var_name = match.group(1)
                value = int(match.group(2)) # On extrait le chiffre décimal
                instructions.append(["ALLOCATE", var_name, value])
                
            # Match: x += 1 OR x = x + 1 (Increment)
            elif match := re.match(r'^([a-zA-Z_]\w*)\s*\+=\s*1$', clean_line) or \
                          re.match(r'^([a-zA-Z_]\w*)\s*=\s*\1\s*\+\s*1$', clean_line):
                var_name = clean_line.split("+=")[0].strip() if "+=" in clean_line else clean_line.split("=")[0].strip()
                instructions.append(["ADD_COUNTER", var_name])
                
            # Match: move(y, x)
            elif match := re.match(r'^move\(([a-zA-Z_]\w*)\s*,\s*([a-zA-Z_]\w*)\)$', clean_line):
                instructions.append(["MOVE", match.group(1), match.group(2)])
                
            else:
                raise SyntaxError(f"Compiler Error: Invalid Python syntax at line -> '{clean_line}'")
                
        return instructions