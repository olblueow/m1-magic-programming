from cards.base import Creature
import cards.factory as factory

class RotlungReanimator(Creature):
    def __init__(self):
        super().__init__("Rotlung Reanimator", 2, 2)
        self.watch_type = "Cleric"
        self.create_type = "Zombie"

    def execute(self, battlefield, annotation="") -> str:
        row, col = map(int, annotation.split(","))
        success = battlefield.place_card(self, row, col)
        
        if success:
            return f"Rotlung Reanimator installed at [{row}, {col}]"
        else:
            return f"Rotlung Reanimator: Collision! Sent to graveyard instead of [{row}, {col}]"

    def trigger(self, died_type: str, battlefield, row: int, col: int) -> str | None:
        if died_type == self.watch_type:
            new_token = factory.create(self.create_type)
            
            # The previous creature just died here, so it SHOULD be empty, 
            # but it's always good practice to check for safety!
            success = battlefield.place_card(new_token, row, col)
            
            if success:
                return f"Trigger: {self.create_type} created at [{row}, {col}]"
            else:
                return f"Trigger: Collision! {self.create_type} sent to graveyard."
                
        return None
    
    def get_rules(self) -> str:
        return f"Whenever a {self.watch_type} dies,\nput a 2/2 {self.create_type} token\ninto play."