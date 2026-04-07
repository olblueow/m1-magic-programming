import time
from logic import ProgramLoader
from engine import Battlefield


def format_memory(battlefield):
    """Generates a string representing the state of the board."""
    creatures_str = []

    for creature in battlefield.get_creatures():
        creatures_str.append(
            f"{creature.token_type}({creature.power}/{creature.toughness})={creature.value()}"
        )

    return "[" + " | ".join(creatures_str) + "]"


def execute_instruction(battlefield, instruction):
    """
    Central execution function (Role 3 integration point).
    Takes parsed instruction and applies it to the engine.
    """

    action = instruction.get("action")
    card = instruction.get("card")
    params = instruction.get("params", {})
    annotation = instruction.get("annotation", "")

    print(f"🔄 Playing card: [{card}]")
    print(f"   Params: {params}")

    # dispatcher-like execution (cleaner than raw if-else in main loop)
    if action == "CONFIG":
        return battlefield.play_artificial_evolution(annotation)

    elif action == "SETUP_CREATE":
        return battlefield.play_setup_create(annotation)

    elif action == "SETUP_PROTECT":
        return battlefield.play_setup_protect(annotation)

    elif action == "EXECUTE":
        return battlefield.play_infest()

    elif action == "MOVE_RIGHT":
        return battlefield.play_bioshift()

    elif action == "MOVE_LEFT":
        return battlefield.play_fate_transfer()

    else:
        return f"Unknown action: {action}"


def main():
    # --- 1. LOADING ---
    cod_file = "data/test_not.cod"

    loader = ProgramLoader(cod_file)
    print(f"Program: {loader.program_name} | Cards: {len(loader.instructions)}\n")

    # --- 2. PREPARATION ---
    battlefield = Battlefield()
    time.sleep(1.0)

    # --- 3. EXECUTION ---
    for step, instruction in enumerate(loader.instructions, 1):
        print(f"\nSTEP {step:02d}")

        result = execute_instruction(battlefield, instruction)

        if result:
            print(f"   Effect: {result}")

        print(f"   Battlefield: {format_memory(battlefield)}")

        time.sleep(0.3)

    # --- 4. RESULT ---
    bits = battlefield.get_memory()

    print("\n=== FINAL RESULT ===")
    print(f"Final state: {format_memory(battlefield)}")

    if bits:
        bin_str = "".join(str(b) for b in bits)
        decimal_val = int(bin_str, 2)
        print(f"Binary: {bin_str} → Decimal: {decimal_val}")


if __name__ == "__main__":
    main()