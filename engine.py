class Battlefield:
    def __init__(self):
        self.permanents = []  # Remplace 'creatures'. Contient les Oozes, Zombies ET le Rotlung.
        self.graveyard = []   # Le cimetière : les créatures mortes et les sorts joués vont ici.
    
    def get_target(self, target_index):
        """Récupère un permanent sur le plateau selon son index."""
        if target_index is None:
            return None
        if target_index < 0 or target_index >= len(self.permanents):
            raise ValueError(f"Cible invalide : aucun permanent à l'index {target_index}")
        return self.permanents[target_index]
    
    def check_state_based_actions(self):
        """Vérifie l'état du plateau : si l'endurance <= 0, la créature meurt."""
        for permanent in self.permanents[:]: # On copie la liste pour pouvoir la modifier
            if hasattr(permanent, 'toughness') and permanent.toughness <= 0:
                self.permanents.remove(permanent)
                self.graveyard.append(permanent)
                print(f"💀 {permanent.token_type} est mort et va au cimetière.")
                
                self.trigger_death_effects(permanent)
    
    def resolve_card(self, card_object, target_index=None):
        """La seule fonction appelée par main.py. Applique l'effet de n'importe quelle carte."""
        target = self.get_target(target_index)
        log = card_object.execute_effect(self, target) 
        
        if card_object.card_type == "Spell":
            self.graveyard.append(card_object)
            
        self.check_state_based_actions()
        return log

    def trigger_death_effects(self, dead_permanent):
        """Prévient tous les permanents du plateau qu'une créature vient de mourir."""
        
        for permanent in self.permanents:
            if hasattr(permanent, 'on_death_trigger'):
                new_token = permanent.on_death_trigger(self, dead_permanent)
                
                if new_token:
                    self.permanents.append(new_token)
                    print(f"✨ Effet déclenché : {permanent.name} a créé un {new_token.token_type} !")