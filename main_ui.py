import tkinter as tk
from tkinter import filedialog
from gui import MagicGUI
from controller import GameController

class Application:
    """
    Main application wrapper. Links the MagicGUI (View) with the GameController (Model).
    Handles file loading, animation loops, and user interaction logic.
    """
    def __init__(self):
        self.root = tk.Tk()
        self.controller = None
        self.is_animating = False
        self.is_auto_playing = False
        
        self.app = MagicGUI(
            self.root, 
            on_next_click=self.on_next, 
            on_auto_click=self.on_auto, 
            on_pause_click=self.on_pause,
            on_load_click=self.load_deck
        )
        self.app.add_log("Please load a .cod file to begin.")

    def load_deck(self):
        """Prompts the user to select a compiled deck file and resets the engine."""
        file_path = filedialog.askopenfilename(
            title="Choose a compiled deck",
            filetypes=[("Cockatrice Deck", "*.cod"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        self.is_auto_playing = False
        self.controller = GameController(file_path)
        self.controller.load()
        
        self.app.reset_playmat(self.controller.get_total_steps())
        
        if self.controller.board is not None:
            self.app.update_board(self.controller.board.grid)
            
        self.app.add_log(f"Deck loaded: {file_path}")

    def on_next(self):
        """Triggers the resolution of a single instruction card from the controller."""
        # Block interaction if no deck is loaded or an animation is already running
        if not self.controller or self.is_animating:
            return

        result = self.controller.next_step()

        if result.get("error"):
            self.app.add_log(result["error"])
            return

        # Ensure the interface ends properly if the user clicks Next after completion
        if result.get("done") and "card" not in result:
            self.is_auto_playing = False
            self.app.finish()
            return

        # 1. ANIMATION START: Show the played card in The Stack
        self.is_animating = True
        self.app.show_in_stack(result["card"], result["annotation"])
        
        # 2. PAUSE: Give the user time to read the card on the Stack (1000ms delay)
        self.root.after(1000, lambda: self.complete_step(result))

    def complete_step(self, result):
        """Finalizes the step resolution, updates the board, and logs the outcome."""
        # Pylance fix: Verify that both controller and board exist before accessing grid
        if self.controller is None or self.controller.board is None:
            return
            
        # 3. RESOLUTION: Render the updated memory tape and CPU states
        self.app.update_board(self.controller.board.grid)
        
        # In Magic, creature cards stay on the battlefield. Spells go to the graveyard.
        if result["card"] == "Rotlung Reanimator":
            self.app.canvas_stack.delete("all")
        else:
            self.app.move_stack_to_graveyard(result["card"])
            
        self.app.set_step(result["step"] + 1, self.controller.get_total_steps())
        self.app.add_log(result["log"])
        
        self.is_animating = False

        # Properly terminate the GUI cycle if this was the last instruction
        if result.get("done"):
            self.is_auto_playing = False
            self.app.finish()

    def on_auto(self):
        """Starts the automated execution loop to run the entire deck."""
        if not self.controller or self.is_animating or self.is_auto_playing:
            return

        self.is_auto_playing = True
        self.app.set_auto_mode(True)

        def loop():
            # Break the loop if the user hit Pause
            if not self.is_auto_playing:
                return
            # Break the loop if the program has finished
            if self.controller is None or self.controller.is_done():
                self.is_auto_playing = False
                self.app.finish()
                return
            
            # Execute next instruction and schedule the next loop iteration (1200ms interval)
            self.on_next()
            self.root.after(1200, loop)

        loop()

    def on_pause(self):
        """Interrupts the Auto Play loop."""
        self.is_auto_playing = False
        self.app.set_auto_mode(False)
        self.app.add_log("Auto Play paused.")

    def run(self):
        """Starts the Tkinter main loop."""
        self.root.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()