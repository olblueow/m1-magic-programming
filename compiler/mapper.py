class SymbolTable:
    def __init__(self, bit_width=4):
        self.variables = {}
        self.next_free_col = 0
        self.bit_width = bit_width

    def allocate(self, var_name: str) -> list:
        if var_name in self.variables:
            raise ValueError(f"Compiler Error: Variable '{var_name}' is already allocated!")
            
        allocated_columns = list(range(self.next_free_col, self.next_free_col + self.bit_width))
        self.variables[var_name] = allocated_columns

        self.next_free_col += self.bit_width 
        
        return self.variables[var_name]

    def get_address_block(self, var_name: str) -> list:
        if var_name not in self.variables:
            raise ValueError(f"Compiler Error: Variable '{var_name}' is not defined!")
        return self.variables[var_name]