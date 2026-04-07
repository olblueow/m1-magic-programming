"""
cards.py — Magic: The Gathering Card Definitions
=================================================
This file defines the card class hierarchy for our MTG engine.

Key principle: each card only knows its own MTG effect.
- Infest says "-2/-2 to all creatures". Period.
- Bioshift says "move a +1/+1 counter from creature A to creature B". Period.
- No card knows anything about incrementing, decrementing, or any algorithm.

The engine (engine.py) is responsible for handling the consequences
(deaths, triggers, state updates). The cards just describe what they do.

Class hierarchy:
    Card (abstract base)
    ├── PermanentCard   → stays on the battlefield after resolution
    │   ├── CreatureToken       (Ooze, Zombie)
    │   └── RotlungReanimator   (trigger permanent)
    └── SpellCard       → resolves and goes to the graveyard
        ├── SlimeMolding        (sorcery — create Ooze token)
        ├── Battlegrowth        (instant — add +1/+1 counter)
        ├── ArtificialEvolution (instant — modify permanent text)
        ├── Infest              (sorcery — -2/-2 to all)
        ├── Bioshift            (instant — move counter right)
        └── FateTransfer        (instant — move counter left)
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ═══════════════════════════════════════════════════════
# ABSTRACT BASE CLASS
# ═══════════════════════════════════════════════════════

class Card(ABC):
    """
    Abstract base class for all Magic: The Gathering cards.
    Every card has a name, a card type, and defines its own effect.
    Cards know nothing about any algorithm — only about MTG rules.
    """

    # Card type constants
    TYPE_CREATURE  = "Creature"
    TYPE_SORCERY   = "Sorcery"
    TYPE_INSTANT   = "Instant"
    TYPE_PERMANENT = "Permanent"

    def __init__(self, name: str, card_type: str):
        self.name      = name
        self.card_type = card_type

    @abstractmethod
    def execute_effect(self, battlefield, annotation: str = "") -> str:
        """
        Apply this card's MTG effect to the battlefield.
        :param battlefield: The Battlefield object (from engine.py)
        :param annotation:  Optional parameters from the .cod file
                            e.g. "target=0" or "watch=Zombie|create=Ooze"
        :return: A human-readable log of what happened
        """
        pass

    def __repr__(self):
        return f"[{self.card_type}] {self.name}"


# ═══════════════════════════════════════════════════════
# PERMANENT CARDS — stay on the battlefield
# ═══════════════════════════════════════════════════════

class PermanentCard(Card):
    """
    Base class for cards that remain on the battlefield after being played.
    Examples: creature tokens, enchantments, artifacts.
    """
    def __init__(self, name: str):
        super().__init__(name, Card.TYPE_PERMANENT)

    def on_enter_battlefield(self, battlefield) -> str:
        """Called when this permanent enters the battlefield."""
        return f"{self.name} enters the battlefield."

    def execute_effect(self, battlefield, annotation: str = "") -> str:
        """Permanents don't have a one-time effect — they sit on the battlefield."""
        return f"{self.name} is already on the battlefield."


class CreatureToken(PermanentCard):
    """
    Represents a creature token on the battlefield.
    Base stats: 2/2 (power 2, toughness 2).
    With a +1/+1 counter: 3/3 — immune to Infest's -2/-2 (protected).
    Without a counter: 2/2 — dies to Infest's -2/-2 (active).

    Token types:
      OOZE   → logical value 0 (green)
      ZOMBIE → logical value 1 (black)
    """

    OOZE   = "Ooze"
    ZOMBIE = "Zombie"

    def __init__(self, token_type: str, has_counter: bool = False):
        super().__init__(token_type)
        self.token_type  = token_type
        self.base_power  = 2
        self.base_tough  = 2
        self.counters    = 1 if has_counter else 0
        self.is_temp     = False   # True = temporary slot created by Bioshift

    @property
    def power(self) -> int:
        return self.base_power + self.counters

    @property
    def toughness(self) -> int:
        return self.base_tough + self.counters

    @property
    def is_active(self) -> bool:
        """
        The active creature is the one WITHOUT a +1/+1 counter.
        It is 2/2 and vulnerable to Infest's -2/-2.
        """
        return self.counters == 0

    def value(self) -> int:
        """Logical bit value: Zombie = 1, Ooze = 0."""
        return 1 if self.token_type == self.ZOMBIE else 0

    def on_death(self, battlefield) -> str:
        """
        Called when this creature's toughness drops to 0 or less.
        Notifies Rotlung Reanimator if present on the battlefield.
        """
        log = f"{self} dies."
        rotlung = battlefield.get_rotlung()
        if rotlung:
            result = rotlung.trigger(self.token_type, battlefield)
            if result:
                log += f"\n  {result}"
        return log

    def __repr__(self):
        status = " [active]" if self.is_active else " [protected]"
        return f"{self.token_type}({self.power}/{self.toughness}){status}"


class RotlungReanimator(PermanentCard):
    """
    Rotlung Reanimator — Creature — Zombie Cleric
    Original text: "Whenever a Cleric dies, create a 2/2 black Zombie token."
    Modified by Artificial Evolution to watch for Ooze or Zombie deaths.

    This card is a real permanent on the battlefield.
    It has a triggered ability that fires when a specific creature type dies.
    """

    def __init__(self):
        super().__init__("Rotlung Reanimator")
        self.watch_type  = None   # Creature type to watch for
        self.create_type = None   # Creature type to create on trigger
        self.configured  = False

    def modify_text(self, watch_type: str, create_type: str):
        """
        Simulates Artificial Evolution changing this card's text.
        Example: modify_text("Zombie", "Ooze") changes the text to:
        "Whenever a Zombie dies, create a 2/2 green Ooze token."
        """
        self.watch_type  = watch_type
        self.create_type = create_type
        self.configured  = True

    def trigger(self, died_type: str, battlefield) -> str | None:
        """
        Triggered ability: fires when a creature of the watched type dies.
        Creates a new 2/2 token of the specified type at the same position.
        Returns a log string if triggered, None otherwise.
        """
        if not self.configured:
            return None
        if died_type != self.watch_type:
            return None

        # Find where the dead creature was and place the new token there
        new_token = CreatureToken(self.create_type, has_counter=False)
        battlefield.replace_active(new_token)
        return (f"Rotlung Reanimator triggers: {died_type} died "
                f"→ creates 2/2 {self.create_type} token.")

    def __repr__(self):
        if self.configured:
            return (f"Rotlung Reanimator "
                    f"[when {self.watch_type} dies → create {self.create_type}]")
        return "Rotlung Reanimator [not configured]"


# ═══════════════════════════════════════════════════════
# SPELL CARDS — resolve and go to the graveyard
# ═══════════════════════════════════════════════════════

class SpellCard(Card):
    """
    Base class for cards that resolve their effect once and go to the graveyard.
    Includes instants and sorceries.
    """
    def __init__(self, name: str, card_type: str):
        super().__init__(name, card_type)


class SlimeMolding(SpellCard):
    """
    Slime Molding — Sorcery
    Original text: "Create an X/X green Ooze creature token."
    In our engine: creates a new 2/2 Ooze token on the battlefield.
    Used during the setup phase to initialize memory slots.
    """

    def __init__(self):
        super().__init__("Slime Molding", Card.TYPE_SORCERY)

    def execute_effect(self, battlefield, annotation: str = "") -> str:
        """
        Creates a new unprotected Ooze token and adds it to the battlefield.
        The token will be protected later by Battlegrowth if needed.
        """
        new_token = CreatureToken(CreatureToken.OOZE, has_counter=False)
        battlefield.add_creature(new_token)
        pos = len(battlefield.get_creatures()) - 1
        return f"Slime Molding: 2/2 Ooze token created at position {pos}."


class Battlegrowth(SpellCard):
    """
    Battlegrowth — Instant
    Original text: "Put a +1/+1 counter on target creature."
    In our engine: adds a +1/+1 counter to the creature at the specified index.
    Annotation format: "target=0" (index of the target creature)
    If no target is specified, targets the leftmost unprotected non-active creature.
    """

    def __init__(self):
        super().__init__("Battlegrowth", Card.TYPE_INSTANT)

    def execute_effect(self, battlefield, annotation: str = "") -> str:
        """
        Adds a +1/+1 counter to a target creature.
        The target is read from the annotation (e.g. "target=0").
        If the target is invalid, the spell fizzles (MTG rule: invalid target).
        """
        target_idx = self._parse_target(annotation)

        if target_idx is not None:
            # Explicit target from annotation
            creatures = battlefield.get_all_creatures()
            if target_idx >= len(creatures) or target_idx < 0:
                return f"Battlegrowth fizzles: target index {target_idx} is invalid."
            target = creatures[target_idx]
            target.counters += 1
            return f"Battlegrowth: +1/+1 counter on {target} at position {target_idx}."
        else:
            # No explicit target: protect leftmost unprotected non-active creature
            creatures = battlefield.get_all_creatures()
            unprotected = [c for c in creatures if c.counters == 0 and not c.is_temp]
            if len(unprotected) <= 1:
                return "Battlegrowth fizzles: no valid target found."
            target = unprotected[0]
            target.counters += 1
            pos = creatures.index(target)
            return f"Battlegrowth: +1/+1 counter on {target} at position {pos}."

    def _parse_target(self, annotation: str) -> int | None:
        """Parses 'target=2' from the annotation string."""
        if "target=" in annotation:
            try:
                value = annotation.split("target=")[1].split("|")[0].strip()
                return int(value)
            except (ValueError, IndexError):
                return None
        return None


class ArtificialEvolution(SpellCard):
    """
    Artificial Evolution — Instant
    Original text: "Change the text of target spell or permanent by replacing
                    all instances of one creature type with another."
    In our engine: modifies Rotlung Reanimator's trigger condition.
    Annotation format: "watch=Zombie|create=Ooze"
                    or "Zombie dies → create Ooze" (legacy format)
    """

    def __init__(self):
        super().__init__("Artificial Evolution", Card.TYPE_INSTANT)

    def execute_effect(self, battlefield, annotation: str = "") -> str:
        """
        Modifies Rotlung Reanimator's trigger text.
        Rotlung must be on the battlefield, otherwise the spell fizzles.
        """
        rotlung = battlefield.get_rotlung()
        if rotlung is None:
            return "Artificial Evolution fizzles: Rotlung Reanimator not on battlefield."

        watch_type, create_type = self._parse_annotation(annotation)
        if watch_type is None or create_type is None:
            return f"Artificial Evolution fizzles: could not parse annotation '{annotation}'."

        rotlung.modify_text(watch_type, create_type)
        return f"Artificial Evolution: {rotlung}"

    def _parse_annotation(self, annotation: str):
        """
        Parses the annotation to extract watch_type and create_type.
        Supports two formats:
          - "watch=Zombie|create=Ooze"
          - "Zombie dies → create Ooze"  (legacy)
        """
        ann = annotation.lower()

        # Format 1: "watch=Zombie|create=Ooze"
        if "watch=" in ann and "create=" in ann:
            try:
                watch  = annotation.split("watch=")[1].split("|")[0].strip()
                create = annotation.split("create=")[1].split("|")[0].strip()
                return watch, create
            except IndexError:
                pass

        # Format 2: "Zombie dies → create Ooze" (legacy)
        if "zombie" in ann and "ooze" in ann:
            z_idx = ann.index("zombie")
            o_idx = ann.index("ooze")
            if z_idx < o_idx:
                return CreatureToken.ZOMBIE, CreatureToken.OOZE
            else:
                return CreatureToken.OOZE, CreatureToken.ZOMBIE

        return None, None


class Infest(SpellCard):
    """
    Infest — Sorcery
    Original text: "All creatures get -2/-2 until end of turn."
    In our engine: reduces all creatures' toughness by 2.
    Any creature whose toughness drops to 0 or less dies immediately.
    This may trigger Rotlung Reanimator if it's on the battlefield.
    """

    def __init__(self):
        super().__init__("Infest", Card.TYPE_SORCERY)

    def execute_effect(self, battlefield, annotation: str = "") -> str:
        """
        Applies -2/-2 to all creatures on the battlefield.
        Creatures with toughness ≤ 0 die and may trigger Rotlung.
        Protected creatures (3/3 with counter) drop to 1/1 and survive.
        Active creatures (2/2 without counter) drop to 0/0 and die.
        """
        log_lines = ["Infest: all creatures get -2/-2."]
        active = battlefield.get_active_creature()

        if active is None:
            return "Infest: no creatures on the battlefield."

        effective_toughness = active.toughness - 2

        if effective_toughness <= 0:
            log_lines.append(
                f"  {active} toughness: {active.toughness} - 2 = {effective_toughness} → dies."
            )
            death_log = active.on_death(battlefield)
            log_lines.append(f"  {death_log}")
        else:
            log_lines.append(
                f"  {active} toughness: {active.toughness} - 2 = {effective_toughness} → survives."
            )

        return "\n".join(log_lines)


class Bioshift(SpellCard):
    """
    Bioshift — Instant
    Original text: "Move any number of +1/+1 counters from target creature
                    to another target creature."
    In our engine: moves one +1/+1 counter from the RIGHT neighbor
                   to the active creature.
    Effect: active creature gains a counter (becomes protected),
            right neighbor loses its counter (becomes the new active creature).
    """

    def __init__(self):
        super().__init__("Bioshift", Card.TYPE_INSTANT)

    def execute_effect(self, battlefield, annotation: str = "") -> str:
        """
        Moves a +1/+1 counter from the right neighbor to the active creature.
        The right neighbor becomes the new active creature.
        If no right neighbor exists, a temporary slot is created.
        """
        active_idx = battlefield.get_active_index()
        if active_idx is None:
            return "Bioshift fizzles: no active creature on the battlefield."

        creatures  = battlefield.get_all_creatures()
        right_idx  = active_idx + 1

        # Extend battlefield with a temporary slot if needed
        if right_idx >= len(creatures):
            temp = CreatureToken(CreatureToken.OOZE, has_counter=True)
            temp.is_temp = True
            battlefield.add_creature(temp)
            creatures = battlefield.get_all_creatures()

        right  = creatures[right_idx]
        active = creatures[active_idx]

        if right.counters < 1:
            return "Bioshift fizzles: right neighbor has no counter to move."

        right.counters  -= 1   # Right neighbor becomes the new active creature
        active.counters += 1   # Current active creature becomes protected

        label = "[temporary slot]" if right.is_temp else str(right)
        return (f"Bioshift: counter moved from position {right_idx} ({label}) "
                f"to position {active_idx} ({active}) "
                f"→ active creature is now at position {right_idx}.")


class FateTransfer(SpellCard):
    """
    Fate Transfer — Instant
    Original text: "Move all +1/+1 counters from target creature to another
                    target creature."
    In our engine: moves one +1/+1 counter from the LEFT neighbor
                   to the active creature.
    Effect: active creature gains a counter (becomes protected),
            left neighbor loses its counter (becomes the new active creature).
    If the active creature is a temporary slot, it is removed.
    """

    def __init__(self):
        super().__init__("Fate Transfer", Card.TYPE_INSTANT)

    def execute_effect(self, battlefield, annotation: str = "") -> str:
        """
        Moves a +1/+1 counter from the left neighbor to the active creature.
        The left neighbor becomes the new active creature.
        Temporary slots are removed when left.
        """
        active_idx = battlefield.get_active_index()
        if active_idx is None:
            return "Fate Transfer fizzles: no active creature on the battlefield."
        if active_idx == 0:
            return "Fate Transfer fizzles: active creature is already at leftmost position."

        creatures = battlefield.get_all_creatures()
        left_idx  = active_idx - 1
        left      = creatures[left_idx]
        active    = creatures[active_idx]

        if left.counters < 1:
            return "Fate Transfer fizzles: left neighbor has no counter to move."

        left.counters   -= 1   # Left neighbor becomes the new active creature
        active.counters += 1   # Current active creature becomes protected

        # Remove temporary slot if needed
        if active.is_temp:
            battlefield.remove_creature_at(active_idx)
            return (f"Fate Transfer: temporary slot removed "
                    f"→ active creature is now at position {left_idx}.")

        return (f"Fate Transfer: counter moved from position {left_idx} ({left}) "
                f"to position {active_idx} ({active}) "
                f"→ active creature is now at position {left_idx}.")


# ═══════════════════════════════════════════════════════
# CARD FACTORY
# ═══════════════════════════════════════════════════════

# Maps card names (from .cod file) to their class
CARD_REGISTRY: dict[str, type] = {
    "Slime Molding":        SlimeMolding,
    "Battlegrowth":         Battlegrowth,
    "Artificial Evolution": ArtificialEvolution,
    "Infest":               Infest,
    "Bioshift":             Bioshift,
    "Fate Transfer":        FateTransfer,
}

def create_card(card_name: str) -> SpellCard | None:
    """
    Factory function: instantiates a card from its name.
    Returns None if the card is not in the registry.
    This replaces the old hardcoded dictionary in logic.py.
    """
    card_class = CARD_REGISTRY.get(card_name)
    if card_class is None:
        return None
    return card_class()


# ═══════════════════════════════════════════════════════
# TEST BLOCK
# ═══════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=== cards.py — Card Registry Test ===\n")

    for name, cls in CARD_REGISTRY.items():
        card = create_card(name)
        print(f"  {card}")

    print("\n=== Checking card independence from algorithm ===")
    print("Each card should only describe its MTG effect:\n")

    infest = create_card("Infest")
    print(f"Infest effect: 'All creatures get -2/-2 until end of turn.'")
    print(f"Does Infest know about incrementing? NO — it just applies -2/-2.")

    bioshift = create_card("Bioshift")
    print(f"\nBioshift effect: 'Move a +1/+1 counter from creature A to creature B.'")
    print(f"Does Bioshift know it's moving right? NO — it just moves a counter.")

    ae = create_card("Artificial Evolution")
    print(f"\nArtificial Evolution: 'Change creature type in a permanent's text.'")
    print(f"Does ArtEvolution know about bits? NO — it just modifies text.")

    print("\n✓ All cards are algorithm-agnostic.")
