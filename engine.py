"""
engine.py — Magic: The Gathering Game Engine
Simulates the physical board rules.
0 = Ooze (Green), 1 = Zombie (Black).
Active memory cell (Head) = 2/2 creature without +1/+1 counter.
Protected memory cells = 3/3 creatures with +1/+1 counter.
"""

OOZE   = "Ooze"
ZOMBIE = "Zombie"

class CreatureToken:
    """Represents a single bit of memory on the board."""
    def __init__(self, token_type: str, has_counter: bool = False):
        self.token_type  = token_type
        self.counters    = 1 if has_counter else 0
        self.is_blank    = False # True for temporary routing slots

    @property
    def power(self) -> int:
        return 2 + self.counters

    @property
    def toughness(self) -> int:
        return 2 + self.counters

    @property
    def is_active(self) -> bool:
        """The active head has no counters (is vulnerable)."""
        return self.counters == 0

    def value(self) -> int:
        """Translates token to binary."""
        return 1 if self.token_type == ZOMBIE else 0


class RotlungReanimator:
    """The ALU: Triggers when a specific creature dies."""
    def __init__(self):
        self.watch_type  = None
        self.create_type = None
        self.is_configured = False

    def configure(self, watch_type: str, create_type: str):
        self.watch_type  = watch_type
        self.create_type = create_type
        self.is_configured = True

    def trigger(self, died_type: str):
        if self.is_configured and died_type == self.watch_type:
            return self.create_type
        return None


class Battlefield:
    """The Game Board."""
    def __init__(self):
        self.creatures = []
        self.rotlung = RotlungReanimator()

    def get_active_index(self):
        """Finds the index of the 2/2 active creature."""
        for i, c in enumerate(self.creatures):
            if c.is_active:
                return i
        return None

    def get_active_position(self):
        """Returns physical position, ignoring blank slots."""
        idx = self.get_active_index()
        return sum(1 for c in self.creatures[:idx] if not c.is_blank) if idx is not None else None

    def get_memory(self):
        """Returns the binary array of the board."""
        return [c.value() for c in self.creatures if not c.is_blank]

    def get_creatures(self):
        """Returns valid tokens for UI display."""
        return [c for c in self.creatures if not c.is_blank]

    # --- CARD EFFECTS (INSTRUCTION SET) ---

    def play_setup_create(self, annotation: str):
        """Slime Molding: Allocates a new Ooze (0)."""
        self.creatures.append(CreatureToken(OOZE, has_counter=False))
        return "Slime Molding: Ooze created"

    def play_setup_protect(self, annotation: str):
        """Battlegrowth: Protects a memory cell (+1/+1)."""
        for c in self.creatures:
            if c.counters == 0 and not c.is_blank:
                # Protect only if it's not the last unprotected one
                unprotected = [x for x in self.creatures if x.counters == 0 and not x.is_blank]
                if len(unprotected) > 1:
                    c.counters += 1
                    return "Battlegrowth: +1/+1 applied"
        return "Battlegrowth: Target failed"

    def play_artificial_evolution(self, annotation: str):
        """Artificial Evolution: Configures the ALU."""
        ann = annotation.lower()
        if "zombie" in ann and "ooze" in ann:
            if ann.index("zombie") < ann.index("ooze"):
                self.rotlung.configure(ZOMBIE, OOZE)
            else:
                self.rotlung.configure(OOZE, ZOMBIE)
            return "Artificial Evolution: ALU Configured"
        return "Artificial Evolution: Error parsing annotation"

    def play_infest(self):
        """Infest: The Clock Cycle (-2/-2)."""
        idx = self.get_active_index()
        if idx is None:
            return "Infest: No active target"

        active = self.creatures[idx]
        died_type = active.token_type
        
        # 2/2 active dies (toughness drops to 0)
        new_type = self.rotlung.trigger(died_type)
        
        if new_type:
            self.creatures[idx] = CreatureToken(new_type, has_counter=False)
            return f"Infest: {died_type} died -> ALU created {new_type}"
        else:
            self.creatures.pop(idx)
            return f"Infest: {died_type} died -> No ALU trigger"

    def play_bioshift(self):
        """Bioshift: Move Right (>>)."""
        idx = self.get_active_index()
        if idx is None: return "Bioshift: Error"

        right_idx = idx + 1
        if right_idx >= len(self.creatures):
            # Create temporary routing slot if out of bounds
            temp = CreatureToken(OOZE, has_counter=True)
            temp.is_blank = True
            self.creatures.append(temp)

        self.creatures[right_idx].counters -= 1
        self.creatures[idx].counters += 1
        return "Bioshift: Head moved RIGHT"

    def play_fate_transfer(self):
        """Fate Transfer: Move Left (<<)."""
        idx = self.get_active_index()
        if idx is None or idx == 0: return "Fate Transfer: Error"

        left_idx = idx - 1
        self.creatures[left_idx].counters -= 1
        self.creatures[idx].counters += 1

        if self.creatures[idx].is_blank:
            self.creatures.pop(idx)
            
        return "Fate Transfer: Head moved LEFT"