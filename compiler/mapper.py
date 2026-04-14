class SymbolTable:
    """Maps human-readable variable names to a physical block of memory (e.g., 4 bits)."""
    
    def __init__(self, bit_width=4):
        self.variables = {}
        self.next_free_col = 0
        self.bit_width = bit_width  # 4 bits par défaut (tu peux le passer à 8 plus tard !)

    def allocate(self, var_name: str) -> list:
        """Assigns a block of consecutive columns for a multi-bit variable."""
        if var_name in self.variables:
            raise ValueError(f"Compiler Error: Variable '{var_name}' is already allocated!")
            
        # On réserve un tableau d'adresses (ex: [0, 1, 2, 3])
        allocated_columns = list(range(self.next_free_col, self.next_free_col + self.bit_width))
        
        self.variables[var_name] = allocated_columns
        
        # Le prochain espace libre sera après ce bloc (+1 case vide pour séparer les variables)
        self.next_free_col += self.bit_width + 1 
        
        return self.variables[var_name]

    def get_address_block(self, var_name: str) -> list:
        """Returns the list of columns assigned to this variable."""
        if var_name not in self.variables:
            raise ValueError(f"Compiler Error: Variable '{var_name}' is not defined!")
            
        return self.variables[var_name]