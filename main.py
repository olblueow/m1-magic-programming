import time
import sys
import os
from logic import ProgramLoader
from engine import Battlefield

def format_memory(battlefield):
    """Crée un affichage détaillé de la mémoire avec les stats des créatures."""
    creatures = battlefield.get_creatures()
    if not creatures:
        return "[]"
    
    parts = []
    for c in creatures:
        # Format : Zombie(3/3)=1 ou Ooze(2/2)=0
        parts.append(f"{c.token_type}({c.power}/{c.toughness})={c.value()}")
    
    return "[" + " | ".join(parts) + "]"

def main():
    print("=" * 65)
    print(" 🃏 MAGIC: THE GATHERING - MOTEUR DE CALCUL (CONSOLE) 🃏")
    print("=" * 65)

    # --- 1. CHARGEMENT DU PROGRAMME ---
    cod_file = "data/increment_0_to_4.cod"
    if len(sys.argv) > 1:
        cod_file = sys.argv[1]

    if not os.path.exists(cod_file):
        print(f"❌ Erreur : Le fichier '{cod_file}' est introuvable.")
        return

    try:
        loader = ProgramLoader(cod_file)
        print(f"📁 Programme chargé : {loader.program_name}")
        print(f"🔢 Nombre de cartes à piocher : {len(loader.instructions)}")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return

    # --- 2. CRÉATION DU PLATEAU VIDE ---
    battlefield = Battlefield()
    
    print("\n⚙️  ÉTAT INITIAL DU PLATEAU")
    print(battlefield)
    print("-" * 65)
    print("\n🚀 DÉBUT DE LA PARTIE (Exécution du Deck)\n")

    time.sleep(1.5)

    # --- 3. BOUCLE D'EXÉCUTION PRINCIPALE ---
    while True:
        instruction = loader.get_next_instruction()
        
        if not instruction: # Plus de cartes à piocher
            break

        action = instruction.get("action")
        card = instruction.get("card")
        annotation = instruction.get("annotation", "")
        step = loader.current_step

        print(f"🔄 ÉTAPE {step:02d} | Pioche : [{card}]")
        
        # Application de l'effet Magic
        log = ""
        if action == "CONFIG":
            log = battlefield.play_artificial_evolution(annotation)
        elif action == "EXECUTE":
            log = battlefield.play_infest()
        elif action == "MOVE_RIGHT":
            log = battlefield.play_bioshift()
        elif action == "MOVE_LEFT":
            log = battlefield.play_fate_transfer()
        elif action == "SETUP_CREATE":
            log = battlefield.play_setup_create(annotation)
        elif action == "SETUP_PROTECT":
            log = battlefield.play_setup_protect(annotation)
        else:
            log = f"⚠️ Action ignorée : {action}"

        # Affichage des logs
        for line in log.split('\n'):
            print(f"   > {line}")

        # Sécurisation de l'affichage de la cible
        cible = battlefield.get_active_position()
        cible_texte = str(cible) if cible is not None else "Aucune"

        # Affichage détaillé de la mémoire !
        memoire_detaillee = format_memory(battlefield)

        print(f"   [Mémoire : {memoire_detaillee} | Cible : {cible_texte}]")
        print("-" * 65)
        
        time.sleep(0.3)

    # --- 4. RÉSULTAT FINAL ---
    final_memory_bits = battlefield.get_memory() # Juste les 0 et 1 pour le calcul
    final_memory_detailed = format_memory(battlefield) # Le bel affichage

    print("\n" + "=" * 65)
    print("🏁 FIN DE LA PARTIE (Plus de cartes dans la bibliothèque)")
    print(f"État physique final : {final_memory_detailed}")
    
    try:
        binary_str = "".join(str(b) for b in final_memory_bits)
        decimal_val = int(binary_str, 2)
        print(f"Valeur binaire lue  : {binary_str} ➔ Valeur décimale : {decimal_val}")
    except ValueError:
        pass

    print("=" * 65)

if __name__ == "__main__":
    main()