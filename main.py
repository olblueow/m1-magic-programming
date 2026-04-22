import tkinter as tk
import os
from tkinter import filedialog
from gui import MagicGUI
from controller import GameController

# Import compiler pipeline
from compiler.lexer import Lexer
from compiler.translator import Translator
from compiler.generator import XMLGenerator

class Application:
    """
    Main application wrapper. Links the View, the Compiler, and the GameController.
    Handles code compilation, file loading, animation loops, and user interactions.
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
            on_load_click=self.prompt_load_deck,
            on_compile_click=self.on_compile 
        )
        self.app.add_log("Welcome to MTG Turing IDE. Write code or load a .cod file to begin.")

    # ── COMPILER PIPELINE ────────────────────────────────────────
    def on_compile(self):
        """Fetches code from the editor, compiles it, and loads the generated .cod file."""
        source_code = self.app.get_editor_code()
        
        if not source_code.strip():
            self.app.set_compiler_status("Error: Source code is empty.", is_error=True)
            return

        try:
            self.app.set_compiler_status("Compiling...")
            
            # 1. Lexical Analysis
            lexer = Lexer()
            tokens = lexer.tokenize(source_code)
            
            # 2. Translation to Magic Cards
            translator = Translator()
            decklist = translator.translate(tokens)
            
            # Pass memory map to the UI to display variables above cards
            self.app.set_variable_map(translator.symbols.variables)
            
            # 3. XML Generation
            if not os.path.exists("data"):
                os.makedirs("data")
            output_path = "data/ide_compiled.cod"
            
            XMLGenerator.build_cod_file(decklist, output_path, "IDE Compiled Script")
            
            self.app.set_compiler_status(f"Success! Compiled {len(decklist)} instructions.\nAutomatically loaded into Visualizer.")
            
            # 4. Automatically load and switch tabs
            self.load_deck(output_path)
            self.app.switch_to_visualizer()
            
        except Exception as e:
            # Catch Syntax Errors and missing variables
            self.app.set_compiler_status(f"Compilation Failed:\n{str(e)}", is_error=True)

    # ── ENGINE & CONTROLLER PIPELINE ──────────────────────────────
    def prompt_load_deck(self):
        """Prompts the user to manually select a compiled deck file."""
        file_path = filedialog.askopenfilename(
            title="Choose a compiled deck",
            filetypes=[("Cockatrice Deck", "*.cod"), ("All Files", "*.*")]
        )
        if file_path:
            # Reset variable map if manually loading a foreign deck
            self.app.set_variable_map({})
            self.load_deck(file_path)

    def load_deck(self, file_path: str):
        """Loads a specific .cod file into the GameController and resets the view."""
        self.is_auto_playing = False
        self.controller = GameController(file_path)
        self.controller.load()
        
        self.app.reset_playmat(self.controller.get_total_steps())
        
        if self.controller.board is not None:
            self.app.update_board(self.controller.board.grid)
            
        self.app.add_log(f"Deck loaded: {file_path}")

    def on_next(self):
        """Triggers the resolution of a single instruction card from the controller."""
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
        
        # 2. PAUSE: Dynamic delay based on the Speed Slider
        delay = self.app.get_delay()
        self.root.after(delay, lambda: self.complete_step(result))

    def complete_step(self, result):
        """Finalizes the step resolution, updates the board, and logs the outcome."""
        if self.controller is None or self.controller.board is None:
            return
            
        # 3. RESOLUTION: Render the updated memory tape and CPU states
        self.app.update_board(self.controller.board.grid)
        
        card_type = result.get("type", "Spell") 
        if card_type == "Creature" or result["card"] == "Rotlung Reanimator":
            self.app.canvas_stack.delete("all")
        else:
            self.app.move_stack_to_graveyard(result["card"])
            
        self.app.set_step(result["step"] + 1, self.controller.get_total_steps())
        self.app.add_log(result["log"])
        
        self.is_animating = False

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
            
            # Execute next instruction and schedule the next loop iteration
            self.on_next()
            # Loop uses the current delay setting dynamically
            self.root.after(self.app.get_delay() + 200, loop)

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