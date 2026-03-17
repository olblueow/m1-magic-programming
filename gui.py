import tkinter as tk

class TuringGUI:
    def __init__(self, root, on_next_click=None):
        """
        Initializes the graphical user interface.
        :param root: The main Tkinter window.
        :param on_next_click: The function (from main.py) to call when the "Next Step" button is clicked.
        """
        self.root = root
        self.root.title("Magic Simulator: Turing Machine (V0)")
        self.root.geometry("800x400")
        self.root.configure(bg="#2c3e50") # Modern dark background

        # --- Title and Legend ---
        title = tk.Label(root, text="Machine Tape (Memory)", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white")
        title.pack(pady=20)

        # --- The Canvas (Drawing Area) ---
        self.canvas = tk.Canvas(root, width=700, height=150, bg="#34495e", highlightthickness=0)
        self.canvas.pack(pady=20)

        # --- The Next Button ---
        # If a function is provided, attach it to the button command
        self.btn_next = tk.Button(root, text="Next Step ⏭️", font=("Arial", 12, "bold"), 
                                  bg="#27ae60", fg="white", padx=20, pady=10, command=on_next_click)
        self.btn_next.pack(pady=10)

        # Drawing configuration variables
        self.cell_size = 80
        self.spacing = 20

    def update_board(self, tape, head_position):
        """
        Clears the canvas and redraws the entire tape based on the new state.
        :param tape: List of 0s and 1s (e.g., [0, 1, 0, 1, 0])
        :param head_position: Index of the reading head (e.g., 2)
        """
        self.canvas.delete("all") # Clear the previous drawing

        # Calculation to center the tape horizontally in the canvas
        total_width = len(tape) * (self.cell_size + self.spacing) - self.spacing
        start_x = (700 - total_width) // 2
        start_y = 35

        for i, value in enumerate(tape):
            x1 = start_x + i * (self.cell_size + self.spacing)
            y1 = start_y
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size

            # Choose color based on 0 or 1 
            bg_color = "#2ecc71" if value == 0 else "#2c2c2c"
            text_val = "0\n" if value == 0 else "1\n"
            text_color = "black" if value == 0 else "white"

            # Choose border (Highlighting the reading head)
            border_thickness = 5 if i == head_position else 1
            border_color = "#e74c3c" if i == head_position else "black" # Red if it's the head

            # Draw the square (cell)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline=border_color, width=border_thickness)
            
            # Draw the text in the center of the cell
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            self.canvas.create_text(center_x, center_y, text=text_val, font=("Arial", 10, "bold"), fill=text_color, justify="center")

# --- Test Block ---
if __name__ == "__main__":
    # This block only runs if gui.py is executed directly (not imported)
    root = tk.Tk()
    
    # 1. Define the sequence of states to simulate the JSON instructions
    # Initial state was: [0, 1, 0, 1, 0] with head at 2
    mock_sequence = [
        {"tape": [0, 1, 1, 1, 0], "head": 2, "desc": "Step 1: WRITE_1 (0 becomes 1)"},
        {"tape": [0, 1, 1, 1, 0], "head": 3, "desc": "Step 2: MOVE_RIGHT (Head moves to index 3)"},
        {"tape": [0, 1, 1, 0, 0], "head": 3, "desc": "Step 3: WRITE_0 (1 becomes 0)"},
        {"tape": [0, 1, 1, 0, 0], "head": 2, "desc": "Step 4: MOVE_LEFT (Head moves to index 2)"}
    ]
    
    # Variable to keep track of where we are in the sequence
    current_test_step = 0

    # 2. Create the mock function for the button
    def test_click():
        global current_test_step
        if current_test_step < len(mock_sequence):
            # Get the current state
            state = mock_sequence[current_test_step]
            
            # Update the GUI
            app.update_board(state["tape"], state["head"])
            print(f"Executed: {state['desc']}")
            
            # Move to the next step
            current_test_step += 1
        else:
            print("End of program reached! No more steps.")

    # 3. Initialize the app
    app = TuringGUI(root, on_next_click=test_click)
    
    # 4. Display the initial state
    print("Initial State Loaded: [0, 1, 0, 1, 0] - Head at 2")
    app.update_board([0, 1, 0, 1, 0], 2)
    
    # 5. Start the window
    root.mainloop()