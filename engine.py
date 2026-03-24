"""
engine.py — Magic: The Gathering Game Engine
=============================================
This module simulates the actual MTG card effects needed to run our program.
There is NO explicit write operation, NO array index manipulation.

Everything is derived from the game state:
  - Creatures have power/toughness and optional +1/+1 counters
  - The active creature is simply the only one WITHOUT a +1/+1 counter (2/2, vulnerable)
  - The memory is the ordered list of all creatures on the battlefield
  - Computation happens through card effects triggering each other

Card effects implemented:
  - Slime Molding      → create a new Ooze token on the battlefield
  - Battlegrowth       → add a +1/+1 counter to a creature (protect it)
  - Artificial Evolution → modify Rotlung Reanimator's trigger condition
  - Infest             → all creatures get -2/-2 until end of turn
  - Bioshift           → move a +1/+1 counter from one creature to another (right)
  - Fate Transfer      → move a +1/+1 counter from one creature to another (left)
  - Rotlung Reanimator → permanent: when a [type] dies, create a 2/2 [token]
"""

OOZE   = "Ooze"
ZOMBIE = "Zombie"


class CreatureToken:
    """
    Represents a creature token on the battlefield.

    Base stats: 2/2 (power 2, toughness 2)
    With +1/+1 counter: effectively 3/3 — immune to Infest's -2/-2 (protected)
    Without counter: stays 2/2 — dies to Infest's -2/-2 (active, unprotected)
    """
    def __init__(self, token_type: str, has_counter: bool = False):
        self.token_type  = token_type   # OOZE or ZOMBIE
        self.base_power  = 2
        self.base_tough  = 2
        self.counters    = 1 if has_counter else 0   # +1/+1 counters
        self.is_blank    = False   # True = temporary slot created by Bioshift

    @property
    def power(self) -> int:
        return self.base_power + self.counters

    @property
    def toughness(self) -> int:
        return self.base_tough + self.counters

    @property
    def is_active(self) -> bool:
        """The active (unprotected) creature is the one without a +1/+1 counter."""
        return self.counters == 0

    def value(self) -> int:
        """Logical bit value: Zombie = 1, Ooze = 0."""
        return 1 if self.token_type == ZOMBIE else 0

    def __repr__(self):
        status = " [ACTIVE]" if self.is_active else " [protected]"
        return f"{self.token_type}({self.power}/{self.toughness}){status}"


class RotlungReanimator:
    """
    Permanent card on the battlefield.
    Original text: "Whenever a Cleric dies, create a 2/2 black Zombie token."
    Modified in real-time by Artificial Evolution to watch Ooze or Zombie deaths.
    """
    def __init__(self):
        self.watch_type  = None   # Token type to watch for
        self.create_type = None   # Token type to create on trigger
        self.configured  = False

    def configure(self, watch_type: str, create_type: str):
        """
        Simulates Artificial Evolution changing Rotlung's text.
        Example: watch_type=ZOMBIE, create_type=OOZE means
        'Whenever a Zombie dies, create a 2/2 green Ooze token.'
        """
        self.watch_type  = watch_type
        self.create_type = create_type
        self.configured  = True

    def trigger(self, died_type: str):
        """
        Called when a creature dies on the battlefield.
        Returns the token type to create, or None if condition not met.
        """
        if self.configured and died_type == self.watch_type:
            return self.create_type
        return None

    def __repr__(self):
        if self.configured:
            return f"Rotlung: when {self.watch_type} dies → create {self.create_type}"
        return "Rotlung: not configured"


class Battlefield:
    """
    The game board. Contains an ordered list of creature tokens.
    The order of creatures defines the memory layout of the program.
    """
    def __init__(self):
        self.creatures: list[CreatureToken] = []
        self.rotlung = RotlungReanimator()

    def setup(self, initial_values: list[int], active_position: int):
        """
        Initializes the battlefield from a list of values and an active position.
        :param initial_values: List of 0s (Ooze) and 1s (Zombie)
        :param active_position: Index of the active (unprotected) creature
        """
        self.creatures = []
        for i, bit in enumerate(initial_values):
            token_type  = ZOMBIE if bit == 1 else OOZE
            has_counter = (i != active_position)
            self.creatures.append(CreatureToken(token_type, has_counter))

    def get_active_index(self):
        """Returns the index of the active creature (no +1/+1 counter)."""
        for i, c in enumerate(self.creatures):
            if c.is_active:
                return i
        return None

    def get_memory(self) -> list[int]:
        """Returns the current memory state as a list of 0s and 1s."""
        return [c.value() for c in self.creatures if not c.is_blank]

    def get_active_position(self):
        """Returns the position of the active creature, excluding temporary slots."""
        active_idx = self.get_active_index()
        if active_idx is None:
            return None
        return sum(1 for c in self.creatures[:active_idx] if not c.is_blank)

    def get_creatures(self) -> list:
        """
        Returns the list of real creature tokens (temporary slots excluded).
        Each token exposes:
          token.token_type  → "Ooze" or "Zombie"
          token.toughness   → 2 (active) or 3 (protected)
          token.counters    → 0 (active) or 1 (protected)
          token.is_active   → True if this is the active creature
          token.value()     → 0 (Ooze) or 1 (Zombie)
        Used by gui.py to render the battlefield.
        """
        return [c for c in self.creatures if not c.is_blank]

    def get_state(self) -> dict:
        """
        Returns a full snapshot of the current game state.
        Useful for gui.py to update the display in one call.
        """
        return {
            "memory":    self.get_memory(),
            "active":    self.get_active_position(),
            "creatures": self.get_creatures(),
            "rotlung":   str(self.rotlung),
        }

    # ── CARD EFFECTS ──────────────────────────────────────────

    def play_setup_create(self, annotation: str) -> str:
        """
        Slime Molding: create a new Ooze token on the battlefield.
        The new token is unprotected by default.
        Battlegrowth will protect the previous tokens during the setup phase.
        """
        new_token = CreatureToken(OOZE, has_counter=False)
        self.creatures.append(new_token)
        pos = len(self.creatures) - 1
        return f"Slime Molding: Ooze created at position {pos} — unprotected (2/2)"

    def play_setup_protect(self, annotation: str) -> str:
        """
        Battlegrowth: add a +1/+1 counter to a creature.
        Protects a memory slot, making it 3/3 (immune to Infest).
        Targets the leftmost unprotected creature that is not the last one
        (the last unprotected creature is the active one — it stays unprotected).
        """
        for c in self.creatures:
            if c.counters == 0 and not c.is_blank:
                unprotected = [x for x in self.creatures if x.counters == 0 and not x.is_blank]
                if len(unprotected) > 1:
                    c.counters += 1
                    pos = self.creatures.index(c)
                    return f"Battlegrowth: +1/+1 counter added to position {pos} → now {c}"
        return "Battlegrowth: no valid target found"

    def play_artificial_evolution(self, annotation: str) -> str:
        """
        Artificial Evolution: modify Rotlung Reanimator's trigger text in real-time.
        Reads the annotation to determine which token type Rotlung now watches,
        and which token type it will create on trigger.
        Format: "Zombie dies → create Ooze"  or  "Ooze dies → create Zombie"
        """
        ann = annotation.lower()
        if "zombie" in ann and "ooze" in ann:
            z_idx = ann.index("zombie")
            o_idx = ann.index("ooze")
            if z_idx < o_idx:
                self.rotlung.configure(ZOMBIE, OOZE)
            else:
                self.rotlung.configure(OOZE, ZOMBIE)
            return f"Artificial Evolution → {self.rotlung}"
        return f"Artificial Evolution → could not parse annotation: '{annotation}'"

    def play_infest(self) -> str:
        """
        Infest: all creatures get -2/-2 until end of turn.
        The active creature (2/2, no counter) drops to 0/0 and dies.
        Protected creatures (3/3, with counter) drop to 1/1 and survive.
        When the active creature dies, Rotlung Reanimator may trigger
        and create a new token in its place.
        """
        log_lines = ["Infest: all creatures get -2/-2"]
        active_idx = self.get_active_index()

        if active_idx is None:
            return "Infest: no active creature found — ERROR"

        active    = self.creatures[active_idx]
        died_type = active.token_type
        effective_toughness = active.toughness - 2

        if effective_toughness <= 0:
            log_lines.append(
                f"  {active} dies (toughness {active.toughness} - 2 = {effective_toughness})"
            )
            new_type = self.rotlung.trigger(died_type)
            if new_type:
                new_token = CreatureToken(new_type, has_counter=False)
                self.creatures[active_idx] = new_token
                log_lines.append(
                    f"  Rotlung triggers: {died_type} died → creates {new_type}"
                )
                log_lines.append(
                    f"  New token at position {active_idx}: {new_token}"
                )
            else:
                self.creatures.pop(active_idx)
                log_lines.append(
                    f"  Rotlung does not trigger (watching {self.rotlung.watch_type})"
                )
        else:
            log_lines.append(
                f"  Active creature survived (toughness {active.toughness} - 2 = {effective_toughness})"
            )

        return "\n".join(log_lines)

    def play_bioshift(self) -> str:
        """
        Bioshift: move a +1/+1 counter from one creature to another.
        Moves the counter from the RIGHT neighbor to the active creature.
        Effect: the active creature gains a counter (becomes protected),
                the right neighbor loses its counter (becomes the new active creature).
        If no right neighbor exists, a temporary unprotected slot is created.
        """
        active_idx = self.get_active_index()
        if active_idx is None:
            return "Bioshift: no active creature found — ERROR"

        right_idx = active_idx + 1

        if right_idx >= len(self.creatures):
            temp = CreatureToken(OOZE, has_counter=True)
            temp.is_blank = True   # Temporary slot — not part of real memory
            self.creatures.append(temp)

        right  = self.creatures[right_idx]
        active = self.creatures[active_idx]

        if right.counters < 1:
            return "Bioshift: right neighbor has no counter to move — ERROR"

        right.counters  -= 1   # Right neighbor becomes the new active creature
        active.counters += 1   # Current active creature becomes protected

        return (f"Bioshift: active creature moves RIGHT to position {right_idx} "
                f"| {'[temporary slot]' if right.is_blank else str(right)}")

    def play_fate_transfer(self) -> str:
        """
        Fate Transfer: move a +1/+1 counter from one creature to another.
        Moves the counter from the LEFT neighbor to the active creature.
        Effect: the active creature gains a counter (becomes protected),
                the left neighbor loses its counter (becomes the new active creature).
        If the active creature was a temporary slot, it is removed.
        """
        active_idx = self.get_active_index()
        if active_idx is None:
            return "Fate Transfer: no active creature found — ERROR"
        if active_idx == 0:
            return "Fate Transfer: active creature is already at leftmost position"

        left_idx = active_idx - 1
        left     = self.creatures[left_idx]
        active   = self.creatures[active_idx]

        if left.counters < 1:
            return "Fate Transfer: left neighbor has no counter to move — ERROR"

        left.counters   -= 1   # Left neighbor becomes the new active creature
        active.counters += 1   # Current active creature becomes protected

        if active.is_blank:
            self.creatures.pop(active_idx)
            return f"Fate Transfer: temporary slot removed | active creature moves LEFT to position {left_idx}"

        return f"Fate Transfer: active creature moves LEFT to position {left_idx}"

    def __repr__(self):
        active_idx = self.get_active_index()
        lines = [f"Battlefield ({len(self.get_creatures())} creatures):"]
        for i, c in enumerate(self.creatures):
            if not c.is_blank:
                marker = " ← ACTIVE" if i == active_idx else ""
                lines.append(f"  [{i}] {c}{marker}")
        lines.append(f"  {self.rotlung}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# TEST BLOCK
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Magic Engine Test — Increment 0 to 4 ===\n")

    bf = Battlefield()

    steps = [
        ("Slime Molding",        "SETUP_CREATE",  "Create Ooze position 0"),
        ("Slime Molding",        "SETUP_CREATE",  "Create Ooze position 1"),
        ("Slime Molding",        "SETUP_CREATE",  "Create Ooze position 2"),
        ("Battlegrowth",         "SETUP_PROTECT", "Protect position 0"),
        ("Battlegrowth",         "SETUP_PROTECT", "Protect position 1"),
        ("Artificial Evolution", "CONFIG",        "Ooze dies → create Zombie"),
        ("Infest",               "EXECUTE",       "position 2: Ooze → Zombie"),
        ("Artificial Evolution", "CONFIG",        "Zombie dies → create Ooze"),
        ("Infest",               "EXECUTE",       "position 2: Zombie → Ooze carry"),
        ("Fate Transfer",        "MOVE_LEFT",     "move left to position 1"),
        ("Artificial Evolution", "CONFIG",        "Ooze dies → create Zombie"),
        ("Infest",               "EXECUTE",       "position 1: Ooze → Zombie carry resolved"),
        ("Bioshift",             "MOVE_RIGHT",    "move right to position 2"),
        ("Artificial Evolution", "CONFIG",        "Ooze dies → create Zombie"),
        ("Infest",               "EXECUTE",       "position 2: Ooze → Zombie"),
        ("Artificial Evolution", "CONFIG",        "Zombie dies → create Ooze"),
        ("Infest",               "EXECUTE",       "position 2: Zombie → Ooze carry"),
        ("Fate Transfer",        "MOVE_LEFT",     "move left to position 1"),
        ("Artificial Evolution", "CONFIG",        "Zombie dies → create Ooze"),
        ("Infest",               "EXECUTE",       "position 1: Zombie → Ooze carry"),
        ("Fate Transfer",        "MOVE_LEFT",     "move left to position 0"),
        ("Artificial Evolution", "CONFIG",        "Ooze dies → create Zombie"),
        ("Infest",               "EXECUTE",       "position 0: Ooze → Zombie carry resolved"),
        ("Bioshift",             "MOVE_RIGHT",    "move right to position 1"),
        ("Bioshift",             "MOVE_RIGHT",    "move right to position 2"),
    ]

    for i, (card, action, note) in enumerate(steps, 1):
        if action == "SETUP_CREATE":
            bf.play_setup_create(note)
        elif action == "SETUP_PROTECT":
            bf.play_setup_protect(note)
        elif action == "CONFIG":
            bf.play_artificial_evolution(note)
        elif action == "EXECUTE":
            bf.play_infest()
        elif action == "MOVE_RIGHT":
            bf.play_bioshift()
        elif action == "MOVE_LEFT":
            bf.play_fate_transfer()

        print(f"Step {i:02d} | {card:25s} | Memory: {bf.get_memory()} | Active: {bf.get_active_position()}")

    print(f"\nFINAL  : {bf.get_memory()}")
    print(f"EXPECTED: [1, 0, 0] (decimal 4)")
    print(f"CORRECT : {'YES ✓' if bf.get_memory() == [1, 0, 0] else 'NO ✗'}")