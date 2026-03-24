"""
engine.py — Magic: The Gathering Game Engine
=============================================
This module simulates the actual MTG rules needed to run our Turing Machine.
There is NO tape index, NO head_position variable, NO explicit write operation.

Everything is derived from the game state:
  - Creatures have power/toughness and optional +1/+1 counters
  - The "Head" is simply the only creature WITHOUT a +1/+1 counter (2/2 = vulnerable)
  - The "Tape" is the ordered list of all creatures on the battlefield
  - Computation happens through card effects triggering each other

Card effects implemented:
  - Infest            → all creatures get -2/-2 until end of turn
  - Bioshift          → move a +1/+1 counter from one creature to another
  - Fate Transfer     → move a +1/+1 counter from one creature to another
  - Artificial Evolution → modify Rotlung Reanimator's trigger condition
  - Rotlung Reanimator → permanent: when a [type] dies, create a 2/2 [token]
"""

OOZE   = "Ooze"
ZOMBIE = "Zombie"


class CreatureToken:
    """
    Represents a creature token on the battlefield.

    Base stats: 2/2 (power 2, toughness 2)
    With +1/+1 counter: effectively 3/3 (immune to Infest's -2/-2)
    Without counter: stays 2/2 (dies to Infest's -2/-2) → this is the HEAD
    """
    def __init__(self, token_type: str, has_counter: bool = False):
        self.token_type  = token_type
        self.base_power  = 2
        self.base_tough  = 2
        self.counters    = 1 if has_counter else 0
        self.is_blank    = False   # True = blank cell added by Bioshift (not real tape)

    @property
    def power(self) -> int:
        return self.base_power + self.counters

    @property
    def toughness(self) -> int:
        return self.base_tough + self.counters

    @property
    def is_head(self) -> bool:
        return self.counters == 0

    def value(self) -> int:
        return 1 if self.token_type == ZOMBIE else 0

    def __repr__(self):
        marker = " [HEAD]" if self.is_head else ""
        blank  = " [blank]" if self.is_blank else ""
        return f"{self.token_type}({self.power}/{self.toughness}){marker}{blank}"


class RotlungReanimator:
    """
    Permanent on the battlefield.
    Original text: "Whenever a Cleric dies, create a 2/2 black Zombie token."
    Modified by Artificial Evolution to watch for Ooze or Zombie deaths.
    """
    def __init__(self):
        self.watch_type  = None
        self.create_type = None
        self.configured  = False

    def configure(self, watch_type: str, create_type: str):
        self.watch_type  = watch_type
        self.create_type = create_type
        self.configured  = True

    def trigger(self, died_type: str):
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
    Order matters: it defines the topology of the Turing Tape.
    """
    def __init__(self):
        self.creatures: list[CreatureToken] = []
        self.rotlung = RotlungReanimator()

    def setup(self, tape: list[int], head_position: int):
        self.creatures = []
        for i, bit in enumerate(tape):
            token_type  = ZOMBIE if bit == 1 else OOZE
            has_counter = (i != head_position)
            self.creatures.append(CreatureToken(token_type, has_counter))

    def get_head_index(self):
        for i, c in enumerate(self.creatures):
            if c.is_head:
                return i
        return None

    def get_tape(self) -> list[int]:
        """Returns the logical tape — blank cells are excluded."""
        return [c.value() for c in self.creatures if not c.is_blank]

    def get_head_position(self):
        """Returns the head position, excluding blank cells from the count."""
        head_idx = self.get_head_index()
        if head_idx is None:
            return None
        return sum(1 for c in self.creatures[:head_idx] if not c.is_blank)

    def get_creatures(self) -> list:
        """
        Returns the list of real creature tokens (blank cells excluded).
        Each token exposes:
          token.token_type  → "Ooze" or "Zombie"
          token.toughness   → 2 (HEAD) or 3 (protected)
          token.counters    → 0 (HEAD) or 1 (protected)
          token.is_head     → True if this is the active HEAD
          token.value()     → 0 (Ooze) or 1 (Zombie)
        Used by gui.py to render the battlefield.
        """
        return [c for c in self.creatures if not c.is_blank]

    def get_state(self) -> dict:
        """
        Returns a full snapshot of the current game state.
        Useful for gui.py to update the display in one call.
        """
        creatures = self.get_creatures()
        return {
            "tape":      self.get_tape(),
            "head":      self.get_head_position(),
            "creatures": creatures,
            "rotlung":   str(self.rotlung),
        }

    # ── CARD EFFECTS ──────────────────────────────────────────

    def play_setup_create(self, annotation: str) -> str:
        """
        Slime Molding: create a new Ooze token on the battlefield.
        Used in the Setup phase to initialize tape cells.
        The new token has no counter by default (will be protected by Battlegrowth).
        """
        new_token = CreatureToken(OOZE, has_counter=False)
        self.creatures.append(new_token)
        pos = len(self.creatures) - 1
        return f"Slime Molding: Ooze(0) created at position {pos}"

    def play_setup_protect(self, annotation: str) -> str:
        """
        Battlegrowth: add a +1/+1 counter to a creature.
        Used in the Setup phase to protect memory cells (make them 3/3).
        Targets the rightmost unprotected non-HEAD token.
        The HEAD (last created, no counter) is always the rightmost.
        We protect the second-to-last token (first unprotected memory cell).
        """
        # Find the first creature without a counter that is NOT the HEAD
        # Strategy: protect creatures from left to right
        for c in self.creatures:
            if c.counters == 0 and not c.is_blank:
                # Check if there's another unprotected creature after it (the real HEAD)
                unprotected = [x for x in self.creatures if x.counters == 0 and not x.is_blank]
                if len(unprotected) > 1:
                    c.counters += 1
                    pos = self.creatures.index(c)
                    return f"Battlegrowth: +1/+1 counter added to position {pos} → now {c}"
        return "Battlegrowth: no target found — ERROR"

    def play_artificial_evolution(self, annotation: str) -> str:
        """
        Artificial Evolution: modify Rotlung Reanimator's trigger text.
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
        return f"Artificial Evolution → could not parse: '{annotation}'"

    def play_infest(self) -> str:
        """
        Infest: all creatures get -2/-2 until end of turn.
        HEAD (2/2, no counter) → 0/0 → dies → Rotlung triggers.
        Protected creatures (3/3) → 1/1 → survive.
        """
        log_lines = ["Infest: all creatures get -2/-2"]
        head_idx  = self.get_head_index()

        if head_idx is None:
            return "Infest: no HEAD found — ERROR"

        head      = self.creatures[head_idx]
        died_type = head.token_type
        effective_toughness = head.toughness - 2

        if effective_toughness <= 0:
            log_lines.append(
                f"  {head} dies (toughness {head.toughness} - 2 = {effective_toughness})"
            )
            new_type = self.rotlung.trigger(died_type)
            if new_type:
                new_token = CreatureToken(new_type, has_counter=False)
                self.creatures[head_idx] = new_token
                log_lines.append(
                    f"  Rotlung triggers: {died_type} died → creates {new_type}"
                )
                log_lines.append(f"  New token at position {head_idx}: {new_token}")
            else:
                self.creatures.pop(head_idx)
                log_lines.append(
                    f"  Rotlung does not trigger (watching {self.rotlung.watch_type})"
                )
        else:
            log_lines.append(
                f"  HEAD survived (toughness {head.toughness} - 2 = {effective_toughness})"
            )

        return "\n".join(log_lines)

    def play_bioshift(self) -> str:
        """
        Bioshift: move +1/+1 counter from RIGHT neighbor to HEAD.
        HEAD moves RIGHT. If no right neighbor exists, create a blank cell.
        """
        head_idx  = self.get_head_index()
        if head_idx is None:
            return "Bioshift: no HEAD found — ERROR"

        right_idx = head_idx + 1

        # Extend tape with a blank cell if needed
        if right_idx >= len(self.creatures):
            blank = CreatureToken(OOZE, has_counter=True)
            blank.is_blank = True   # Mark as temporary blank — not real tape data
            self.creatures.append(blank)

        right = self.creatures[right_idx]
        head  = self.creatures[head_idx]

        if right.counters < 1:
            return "Bioshift: right neighbor has no counter to move — ERROR"

        right.counters -= 1   # Right loses counter → becomes new HEAD
        head.counters  += 1   # Head gains counter → becomes protected memory

        return (f"Bioshift: HEAD moves RIGHT to {right_idx} "
                f"| {'[blank cell]' if right.is_blank else str(right)}")

    def play_fate_transfer(self) -> str:
        """
        Fate Transfer: move +1/+1 counter from LEFT neighbor to HEAD.
        HEAD moves LEFT.
        If HEAD was a blank cell (created by Bioshift), it is removed.
        """
        head_idx = self.get_head_index()
        if head_idx is None:
            return "Fate Transfer: no HEAD found — ERROR"
        if head_idx == 0:
            return "Fate Transfer: HEAD is already at leftmost position — no move"

        left_idx = head_idx - 1
        left     = self.creatures[left_idx]
        head     = self.creatures[head_idx]

        if left.counters < 1:
            return "Fate Transfer: left neighbor has no counter to move — ERROR"

        # Move counter: left → head
        left.counters -= 1   # Left becomes new HEAD
        head.counters += 1   # Head becomes protected memory

        # If current HEAD was a blank cell, remove it now (it was temporary)
        if head.is_blank:
            self.creatures.pop(head_idx)
            return f"Fate Transfer: blank cell removed | HEAD moves LEFT to {left_idx}"

        return (f"Fate Transfer: HEAD moves LEFT to {left_idx}")

    def __repr__(self):
        head_idx = self.get_head_index()
        lines = [f"Battlefield ({len(self.creatures)} tokens):"]
        for i, c in enumerate(self.creatures):
            marker = " ← HEAD" if i == head_idx else ""
            lines.append(f"  [{i}] {c}{marker}")
        lines.append(f"  {self.rotlung}")
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# TEST BLOCK
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Magic Engine Test — Binary Increment 011 → 100 ===\n")

    bf = Battlefield()
    bf.setup(tape=[0, 1, 1], head_position=0)
    print(bf)

    steps = [
        ("Bioshift",             "MOVE_RIGHT",  "q0: tape[0]=Ooze, no write"),
        ("Bioshift",             "MOVE_RIGHT",  "q0: tape[1]=Zombie, no write"),
        ("Bioshift",             "MOVE_RIGHT",  "q0: tape[2]=Zombie → blank"),
        ("Fate Transfer",        "MOVE_LEFT",   "q0→q1: blank reached, move left"),
        ("Artificial Evolution", "CONFIG",      "Zombie dies → create Ooze"),
        ("Infest",               "EXECUTE",     "q1: tape[2] Zombie→Ooze"),
        ("Fate Transfer",        "MOVE_LEFT",   "q1: move left"),
        ("Artificial Evolution", "CONFIG",      "Zombie dies → create Ooze"),
        ("Infest",               "EXECUTE",     "q1: tape[1] Zombie→Ooze"),
        ("Fate Transfer",        "MOVE_LEFT",   "q1: move left"),
        ("Artificial Evolution", "CONFIG",      "Ooze dies → create Zombie"),
        ("Infest",               "EXECUTE",     "q1→qhalt: tape[0] Ooze→Zombie"),
    ]

    for i, (card, action, note) in enumerate(steps, 1):
        print(f"\nStep {i:02d} | {card} | {note}")
        if action == "MOVE_RIGHT":
            print(" ", bf.play_bioshift())
        elif action == "MOVE_LEFT":
            print(" ", bf.play_fate_transfer())
        elif action == "CONFIG":
            print(" ", bf.play_artificial_evolution(note))
        elif action == "EXECUTE":
            print(" ", bf.play_infest())
        print(f"  Tape: {bf.get_tape()} | Head: {bf.get_head_position()}")

    print(f"\nFINAL TAPE : {bf.get_tape()}")
    print(f"EXPECTED   : [1, 0, 0] (binary 100 = 4)")
    result = bf.get_tape()
    print(f"CORRECT    : {'YES ✓' if result == [1, 0, 0] else 'NO ✗'}")