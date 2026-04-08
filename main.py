from logic import ProgramLoader
from engine import Battlefield
import cards.factory as factory

def main():
    loader = ProgramLoader("data/test_100_bits.cod")
    battlefields = Battlefield()
    
    for step, inst in enumerate(loader.instructions, 1):
        card = factory.create(inst["card"])
        if not card:
            print("Card not found:", inst["card"])
            continue

        log = battlefields.resolve(card, inst["annotation"])
        if card.type != "Token": 
            print(f"[{step:03d}] {card.name} -> {log}")

    bits = []
    for creature in battlefields.memory:
        if creature is not None:
            if creature.name == "Zombie":
                bits.append(1)
            elif creature.name == "Ooze":
                bits.append(0)
    
    binary_str = "".join(str(b) for b in bits)

    print(f"\nTape (Binary) : {binary_str}")

if __name__ == "__main__":
    main()