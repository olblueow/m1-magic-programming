import tkinter as tk
from logic import ProgramLoader
from engine import Battlefield
from gui import TuringGUI

def main():
    # --- Load the .cod program ---
    try:
        loader = ProgramLoader("data/binary_increment.cod")
        print(f"Program loaded : {loader.program_name}")
        print(f"Tape           : {loader.tape}")
        print(f"Head position  : {loader.head_position}")
        print(f"Total steps    : {len(loader.instructions)}")
    except Exception as e:
        print(f"Error loading program: {e}")
        return

    # --- Initialize the Magic battlefield ---
    # If the .cod has a SETUP phase (Slime Molding / Battlegrowth),
    # the battlefield starts empty and cards build it progressively.
    # Otherwise, setup from tape metadata in <comments>.
    battlefield = Battlefield()
    has_setup_cards = any(i.get("action") in ("SETUP_CREATE", "SETUP_PROTECT")
                          for i in loader.instructions)
    if not has_setup_cards:
        battlefield.setup(loader.tape, loader.head_position)
    print(f"\nInitial battlefield:")
    print(battlefield)
    print()

    # --- Create the main window ---
    root = tk.Tk()

    # --- Controller: one card played per click ---
    def handle_next_step():
        instruction = loader.get_next_instruction()

        if instruction:
            action     = instruction.get("action")
            card       = instruction.get("card")
            annotation = instruction.get("annotation", "")

            print(f"\n── Step {loader.current_step:02d} | Playing: [{card}] ──")

            # ── Apply the real MTG card effect ──────────────────────
            if action == "CONFIG":
                # Artificial Evolution: reprogram Rotlung Reanimator
                log = battlefield.play_artificial_evolution(annotation)

            elif action == "EXECUTE":
                # Infest: -2/-2 to all → HEAD dies → Rotlung triggers
                log = battlefield.play_infest()

            elif action == "MOVE_RIGHT":
                # Bioshift: move +1/+1 counter right → HEAD shifts right
                log = battlefield.play_bioshift()

            elif action == "MOVE_LEFT":
                # Fate Transfer: move +1/+1 counter left → HEAD shifts left
                log = battlefield.play_fate_transfer()

            elif action == "SETUP_CREATE":
                # Slime Molding: create a new Ooze token (Setup phase)
                log = battlefield.play_setup_create(annotation)

            elif action == "SETUP_PROTECT":
                # Battlegrowth: add +1/+1 counter to protect a memory cell
                log = battlefield.play_setup_protect(annotation)

            else:
                log = f"Unknown action: {action}"

            print(log)

            # ── Read the new game state (derived from creature objects) ──
            tape         = battlefield.get_tape()
            head_pos     = battlefield.get_head_position()

            print(f"Tape : {tape}  |  Head : {head_pos}")

            # ── Update the GUI ──
            app.update_board(tape, head_pos, instruction)

        else:
            # No more cards in the deck → program finished
            tape     = battlefield.get_tape()
            head_pos = battlefield.get_head_position()
            print("\n" + "=" * 50)
            print(f"Program finished.")
            print(f"Final tape : {tape}")
            print(f"Binary     : {''.join(str(b) for b in tape)}")
            print(f"Decimal    : {int(''.join(str(b) for b in tape), 2)}")
            print("=" * 50)
            app.btn_next.config(text="Program Finished ✓", state=tk.DISABLED)

    # --- Initialize GUI ---
    app = TuringGUI(root, on_next_click=handle_next_step)

    # --- Display initial state ---
    app.update_board(battlefield.get_tape(), battlefield.get_head_position())
    print("Initial state displayed.")

    # --- Start ---
    root.mainloop()


if __name__ == "__main__":
    main()