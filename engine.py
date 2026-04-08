class Battlefield:
    def __init__(self):
        self.memory = []
        self.processor = []
        self.graveyard = []

    def resolve(self, card, annotation=""):
        log = card.execute(self, annotation)
        if card.type == "Spell":
            self.graveyard.append(card)
        self.check_deaths()
        return log

    def check_deaths(self):
        for index, creature in enumerate(self.memory):
            if creature and creature.toughness <= 0:
                self.memory[index] = None
                self.graveyard.append(creature)
                # Notify processors (like Rotlung)
                for proc in self.processor:
                    proc.trigger(creature.name, self, index)