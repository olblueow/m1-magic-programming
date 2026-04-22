import pkgutil
import importlib
import cards.spells
import cards.creatures
from cards.base import Card

REGISTRY = {}

# 1. Open all files in the folders automatically
for folder in [cards.spells, cards.creatures]:
    for _, module_name, _ in pkgutil.iter_modules(folder.__path__):
        importlib.import_module(f"{folder.__name__}.{module_name}")

# 2. Register every card found
def get_all_subclasses(parent):
    """Recursively find all children, grandchildren, etc."""
    all_cards = []
    for child in parent.__subclasses__():
        all_cards.append(child)
        all_cards.extend(get_all_subclasses(child))
    return all_cards

for card_class in get_all_subclasses(Card):
    try:
        temp_instance = card_class() # type: ignore
        REGISTRY[temp_instance.name] = card_class
    except Exception as e:
            print(f"Warning: Failed to load card class {card_class.__name__} - {e}")

def create(name: str):
    """Create a new card instance by its name."""
    if name in REGISTRY:
        return REGISTRY[name]()
    return None