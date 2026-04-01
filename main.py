import time
from logic import ProgramLoader
from engine import Battlefield

def format_memory(battlefield):
    """Generates a string representing the state of the board."""
    creatures_str = []
    
    # We loop through the creatures and format their stats nicely
    for creature in battlefield.get_creatures():
        creatures_str.append(f"{creature.token_type}({creature.power}/{creature.toughness})={creature.value()}")
        
    return "[" + " | ".join(creatures_str) + "]"

def main():
    # --- 1. LOADING ---
    cod_file = "data/increment_0_to_4.cod"
    loader = ProgramLoader(cod_file)
    print(f"Program: {loader.program_name} | Cards: {len(loader.instructions)}\n")

    # --- 2. PREPARATION ---
    battlefield = Battlefield()
    time.sleep(1.5)

    # --- 3. EXECUTION ---
    for step, instruction in enumerate(loader.instructions, 1):
        action = instruction.get("action")
        card = instruction.get("card")
        annotation = instruction.get("annotation", "")

        print(f"🔄 STEP {step:02d} | Draw: [{card}]")
        
        # Simple if/elif block to trigger the right Magic card effect
        if action == "CONFIG":
            battlefield.play_artificial_evolution(annotation)
        elif action == "SETUP_CREATE":
            battlefield.play_setup_create(annotation)
        elif action == "SETUP_PROTECT":
            battlefield.play_setup_protect(annotation)
        elif action == "EXECUTE":
            battlefield.play_infest()
        elif action == "MOVE_RIGHT":
            battlefield.play_bioshift()
        elif action == "MOVE_LEFT":
            battlefield.play_fate_transfer()

        # Display the detailed memory and the target
        print(f"   Battlefield: {format_memory(battlefield)}")
        print("")
        
        time.sleep(0.3)

    # --- 4. RESULT ---
    bits = battlefield.get_memory()
    print(f"END OF GAME | Final physical state: {format_memory(battlefield)}")
    
    # Calculate the decimal value if the memory is not empty
    if bits:
        bin_str = "".join(str(b) for b in bits)
        decimal_val = int(bin_str, 2)
        print(f"Binary value read: {bin_str} ➔ Decimal value: {decimal_val}\n")

if __name__ == "__main__":
    main()