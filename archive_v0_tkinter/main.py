import tkinter as tk
from logic import ProgramLoader
from archive_v0_tkinter.gui import TuringGUI

def main():
    # Load the JSON program (Model)
    try:
        loader = ProgramLoader("data/test_increment.json")
        print("Program loaded successfully.")
    except Exception as e:
        print(f"Error loading program: {e}")
        return

    # Create the main window (View)
    root = tk.Tk()
    
    # Define the Controller logic (What happens when we click 'Next')
    def handle_next_step():
        # Fetch the next instruction from the loader
        instruction = loader.get_next_instruction()
        
        if instruction:
            action = instruction.get("action")
            
            # --- The "CPU" logic: Applying the instruction to the state ---
            if action == "WRITE_1":
                loader.tape[loader.head_position] = 1
            elif action == "WRITE_0":
                loader.tape[loader.head_position] = 0
            elif action == "MOVE_RIGHT":
                # Ensure we don't go out of bounds
                if loader.head_position < len(loader.tape) - 1:
                    loader.head_position += 1
            elif action == "MOVE_LEFT":
                if loader.head_position > 0:
                    loader.head_position -= 1
            
            # Print to console for debugging
            print(f"Executed: {instruction['description']} | New Head Pos: {loader.head_position}")
            
            # Update the graphical interface with the new state
            app.update_board(loader.tape, loader.head_position)
            
        else:
            print("End of program. No more instructions.")
            # Disable the button or change its text
            app.btn_next.config(text="Program Finished", state=tk.DISABLED)

    # Initialize the GUI and link the button to our controller function
    app = TuringGUI(root, on_next_click=handle_next_step)
    
    # Draw the initial state on the screen before the first click
    app.update_board(loader.tape, loader.head_position)
    print(f"Initial State Displayed. Tape: {loader.tape}, Head at: {loader.head_position}")
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()