class GameEngine:
    def __init__(self, battlefield):
        self.battlefield = battlefield

    def resolve(self, card, annotation=""):
        # 1. Résolution de la carte
        log = card.execute(self.battlefield, annotation)
        if card.type == "Spell":
            self.battlefield.graveyard.append(card)
            
        # 2. On vérifie qui est mort (State-Based Actions)
        self.check_state_based_actions()
        
        # 3. NOUVEAU : On soigne tout le monde (Fin de l'étape / Tour)
        self.cleanup_step()
        
        return log

    def check_state_based_actions(self):
        dead = [] # Stocke (row, col, creature)

        # On utilise .items() pour scanner sans modifier en direct
        for (row, col), creature in list(self.battlefield.grid.items()):
            # La magie des @property : creature.toughness est calculée en temps réel !
            if creature and hasattr(creature, 'toughness') and creature.toughness <= 0:
                self.battlefield.grid.pop((row, col))
                self.battlefield.graveyard.append(creature)
                dead.append((row, col, creature))

        # Les processeurs réagissent aux morts
        for row, col, creature in dead:
            processors = [c for (r, c_idx), c in self.battlefield.grid.items() if r == 1]
            for proc in processors:
                # Attention : le Rotlung crée la nouvelle carte à la place du mort (row, col)
                proc.trigger(creature.name, self.battlefield, row, col)

    def cleanup_step(self):
        """La fameuse Cleanup Step de Magic The Gathering."""
        for creature in self.battlefield.grid.values():
            if hasattr(creature, 'cleanup_end_of_turn'):
                creature.cleanup_end_of_turn()