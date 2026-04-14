import tkinter as tk

# ─────────────────────────────────────────────────────────────
# COLOR SCHEME
# ─────────────────────────────────────────────────────────────
BG_MAIN      = "#1a1a2e"   # Dark navy background
BG_PANEL     = "#16213e"   # Slightly lighter panel
BG_CARD_INFO = "#0f3460"   # Deep blue card info bar
BG_CANVAS    = "#16213e"   # Canvas background

# Cell colors
COLOR_OOZE    = "#2ecc71"  # Green  — logical 0
COLOR_ZOMBIE  = "#2c3e50"  # Dark   — logical 1
COLOR_ROTLUNG = "#8e44ad"  # Purple — processor
COLOR_ACTIVE  = "#e74c3c"  # Red    — active creature (no counter)
COLOR_EMPTY   = "#1a1a2e"  # Empty slot

# Card type colors
CARD_COLORS = {
    "Slime Molding":        "#27ae60",   # Green   — create token
    "Battlegrowth":         "#16a085",   # Teal    — add counter
    "Artificial Evolution": "#8e44ad",   # Purple  — reprogram
    "Infest":               "#c0392b",   # Red     — destroy
    "Bioshift":             "#2980b9",   # Blue    — move right
    "Fate Transfer":        "#2471a3",   # Blue    — move left
    "Murder":               "#922b21",   # Dark red — kill
    "Giant Growth":         "#1e8449",   # Dark green — buff
    "Rotlung Reanimator":   "#6c3483",   # Dark purple — processor
}

TEXT_MUTED   = "#7f8c8d"
TEXT_PRIMARY = "#ecf0f1"
TEXT_ACCENT  = "#f39c12"


class MagicGUI:
    """
    Role 1 — Visual shell for the Magic MTG simulator.
    Manages aesthetics, layout, and drawing only.
    Does NOT contain any game logic.

    Public interface for Role 2 to call:
      gui.update_board(grid)           → redraws the entire battlefield
      gui.add_log(message)             → adds a line to the log area
      gui.set_card_played(name, annot) → updates the card info panel
      gui.set_step(n, total)           → updates the step counter
      gui.finish()                     → disables buttons, shows done state
    """

    def __init__(self, root, on_next_click=None, on_auto_click=None):
        self.root = root
        self.root.title("Magic: The Gathering — Computation Engine")
        self.root.geometry("1000x700")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(True, True)

        self.cell_size = 90
        self.cell_gap  = 12
        self.step_count = 0

        self._build_layout(on_next_click, on_auto_click)

    # ── LAYOUT BUILDER ────────────────────────────────────────

    def _build_layout(self, on_next_click, on_auto_click):
        """Builds the 3-zone layout: top log, center canvas, bottom controls."""

        # ── TOP: Title + Log area ──────────────────────────────
        top_frame = tk.Frame(self.root, bg=BG_MAIN)
        top_frame.pack(fill="x", padx=20, pady=(15, 0))

        tk.Label(
            top_frame,
            text="⚙  Magic Computation Engine",
            font=("Courier New", 15, "bold"),
            bg=BG_MAIN, fg=TEXT_ACCENT
        ).pack(side="left")

        self.lbl_step = tk.Label(
            top_frame,
            text="Step 0 / —",
            font=("Courier New", 11),
            bg=BG_MAIN, fg=TEXT_MUTED
        )
        self.lbl_step.pack(side="right")

        # Log area
        log_frame = tk.Frame(self.root, bg=BG_PANEL, bd=0)
        log_frame.pack(fill="x", padx=20, pady=(8, 0))

        self.log_text = tk.Text(
            log_frame,
            height=5,
            bg=BG_PANEL, fg="#a9cce3",
            font=("Courier New", 9),
            relief="flat",
            state="disabled",
            wrap="word",
            padx=10, pady=6
        )
        self.log_text.pack(fill="x")

        # Scrollbar for log
        log_scroll = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        # ── CENTER: Card info + Canvas ─────────────────────────
        center_frame = tk.Frame(self.root, bg=BG_MAIN)
        center_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Card info bar
        card_bar = tk.Frame(center_frame, bg=BG_CARD_INFO, pady=0)
        card_bar.pack(fill="x", pady=(0, 8))

        self.lbl_card_name = tk.Label(
            card_bar,
            text="▶  — waiting —",
            font=("Arial", 12, "bold"),
            bg=BG_CARD_INFO, fg=TEXT_ACCENT,
            anchor="w", padx=16, pady=8
        )
        self.lbl_card_name.pack(side="left")

        self.lbl_card_type = tk.Label(
            card_bar,
            text="",
            font=("Arial", 10),
            bg=BG_CARD_INFO, fg=TEXT_MUTED,
            anchor="e", padx=16, pady=8
        )
        self.lbl_card_type.pack(side="left")

        self.lbl_annotation = tk.Label(
            card_bar,
            text="",
            font=("Courier New", 10),
            bg=BG_CARD_INFO, fg="#85c1e9",
            anchor="e", padx=16, pady=8
        )
        self.lbl_annotation.pack(side="right")

        # Row labels
        rows_label_frame = tk.Frame(center_frame, bg=BG_MAIN)
        rows_label_frame.pack(fill="x")

        self.lbl_row0 = tk.Label(
            rows_label_frame,
            text="ROW 0 — Memory (Ooze / Zombie tokens)",
            font=("Courier New", 9),
            bg=BG_MAIN, fg=TEXT_MUTED, anchor="w"
        )
        self.lbl_row0.pack(fill="x", pady=(0, 2))

        # Canvas row 0 (memory)
        self.canvas_row0 = tk.Canvas(
            center_frame,
            height=self.cell_size + 40,
            bg=BG_CANVAS,
            highlightthickness=1,
            highlightbackground="#2c3e50"
        )
        self.canvas_row0.pack(fill="x", pady=(0, 8))

        self.lbl_row1 = tk.Label(
            rows_label_frame,
            text="ROW 1 — Processors (Rotlung Reanimator)",
            font=("Courier New", 9),
            bg=BG_MAIN, fg=TEXT_MUTED, anchor="w"
        )

        # Canvas row 1 (processors)
        self.canvas_row1 = tk.Canvas(
            center_frame,
            height=self.cell_size + 40,
            bg=BG_CANVAS,
            highlightthickness=1,
            highlightbackground="#2c3e50"
        )
        self.canvas_row1.pack(fill="x", pady=(0, 8))

        # ── BOTTOM: Controls + Legend ──────────────────────────
        bottom_frame = tk.Frame(self.root, bg=BG_MAIN)
        bottom_frame.pack(fill="x", padx=20, pady=(0, 15))

        # Buttons
        btn_frame = tk.Frame(bottom_frame, bg=BG_MAIN)
        btn_frame.pack(side="left")

        self.btn_next = tk.Button(
            btn_frame,
            text="▶  Next Step",
            font=("Arial", 11, "bold"),
            bg="#27ae60", fg="white",
            padx=20, pady=8,
            relief="flat",
            cursor="hand2",
            command=on_next_click
        )
        self.btn_next.pack(side="left", padx=(0, 10))

        self.btn_auto = tk.Button(
            btn_frame,
            text="⏩  Auto Play",
            font=("Arial", 11, "bold"),
            bg="#2980b9", fg="white",
            padx=20, pady=8,
            relief="flat",
            cursor="hand2",
            command=on_auto_click
        )
        self.btn_auto.pack(side="left", padx=(0, 10))

        self.btn_pause = tk.Button(
            btn_frame,
            text="⏸  Pause",
            font=("Arial", 11, "bold"),
            bg="#e67e22", fg="white",
            padx=20, pady=8,
            relief="flat",
            cursor="hand2",
            state="disabled"
        )
        self.btn_pause.pack(side="left")

        # Legend
        legend_frame = tk.Frame(bottom_frame, bg=BG_MAIN)
        legend_frame.pack(side="right")

        legend_items = [
            (COLOR_OOZE,    "Ooze (0)"),
            (COLOR_ZOMBIE,  "Zombie (1)"),
            (COLOR_ACTIVE,  "Active"),
            (COLOR_ROTLUNG, "Rotlung"),
            ("#555555",     "Empty"),
        ]
        for color, label in legend_items:
            f = tk.Frame(legend_frame, bg=BG_MAIN)
            f.pack(side="left", padx=6)
            tk.Frame(f, bg=color, width=14, height=14).pack(side="left")
            tk.Label(
                f, text=label,
                font=("Arial", 8),
                bg=BG_MAIN, fg=TEXT_MUTED
            ).pack(side="left", padx=3)

    # ── PUBLIC INTERFACE FOR ROLE 2 ───────────────────────────

    def update_board(self, grid: list):
        """
        Redraws the entire battlefield based on the grid.
        :param grid: 2D list from Battlefield — grid[row][col] = creature or None
                     Row 0 = memory tokens, Row 1 = processors
        """
        self.canvas_row0.delete("all")
        self.canvas_row1.delete("all")

        if not grid:
            return

        row0 = grid[0] if len(grid) > 0 else []
        row1 = grid[1] if len(grid) > 1 else []

        self._draw_row(self.canvas_row0, row0, show_addresses=True)
        self._draw_row(self.canvas_row1, row1, show_addresses=False)

    def _draw_row(self, canvas, row: list, show_addresses: bool = True):
        """Draws a single row of creature cells on the given canvas."""
        if not row:
            canvas.create_text(
                10, (self.cell_size + 40) // 2,
                text="(empty)",
                font=("Courier New", 9),
                fill=TEXT_MUTED,
                anchor="w"
            )
            return

        canvas_width = canvas.winfo_width() or 960
        total_width  = len(row) * (self.cell_size + self.cell_gap) - self.cell_gap
        start_x      = max(10, (canvas_width - total_width) // 2)
        start_y      = 30

        for col, creature in enumerate(row):
            x1 = start_x + col * (self.cell_size + self.cell_gap)
            y1 = start_y
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size

            self._draw_cell(canvas, x1, y1, x2, y2, creature, col, show_addresses)

    def _draw_cell(self, canvas, x1, y1, x2, y2, creature, col_idx, show_address):
        """Draws a single cell with the appropriate color, text, and border."""
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        if creature is None:
            # Empty slot
            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=COLOR_EMPTY, outline="#2c3e50", width=1, dash=(4, 4)
            )
            canvas.create_text(cx, cy, text="—", font=("Arial", 10), fill="#555")

        else:
            name = creature.name if hasattr(creature, 'name') else str(creature)

            # Choose color
            if name == "Ooze":
                bg_color   = COLOR_OOZE
                text_color = "#1a5c34"
                label      = f"Ooze\n0"
            elif name == "Zombie":
                bg_color   = COLOR_ZOMBIE
                text_color = "white"
                label      = f"Zombie\n1"
            elif "Rotlung" in name:
                bg_color   = COLOR_ROTLUNG
                text_color = "white"
                label      = "Rotlung\nReanimator"
            else:
                bg_color   = "#7f8c8d"
                text_color = "white"
                label      = name

            # Border: red if active (no counter), normal otherwise
            is_active    = hasattr(creature, 'counters') and creature.counters == 0
            border_color = COLOR_ACTIVE if is_active else "#2c3e50"
            border_width = 3 if is_active else 1

            # Draw cell
            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=bg_color,
                outline=border_color,
                width=border_width
            )

            # Draw creature name + value
            canvas.create_text(
                cx, cy - 6,
                text=label,
                font=("Arial", 9, "bold"),
                fill=text_color,
                justify="center"
            )

            # Draw stats (power/toughness + counters)
            if hasattr(creature, 'power') and hasattr(creature, 'toughness'):
                stats = f"{creature.power}/{creature.toughness}"
                if hasattr(creature, 'counters') and creature.counters > 0:
                    stats += f"  +{creature.counters}"
                canvas.create_text(
                    cx, y2 - 10,
                    text=stats,
                    font=("Courier New", 8),
                    fill=text_color
                )

        # Memory address label above cell
        if show_address:
            canvas.create_text(
                (x1 + x2) / 2, y1 - 14,
                text=f"[{col_idx}]",
                font=("Courier New", 8),
                fill=TEXT_MUTED
            )

    def add_log(self, message: str):
        """Appends a message to the log area."""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"  {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def set_card_played(self, card_name: str, annotation: str = ""):
        """Updates the card info panel with the currently played card."""
        color = CARD_COLORS.get(card_name, TEXT_ACCENT)
        self.lbl_card_name.config(text=f"▶  {card_name}", fg=color)
        self.lbl_annotation.config(text=annotation if annotation else "")

    def set_step(self, current: int, total: int):
        """Updates the step counter label."""
        self.step_count = current
        self.lbl_step.config(text=f"Step {current} / {total}")

    def set_card_type(self, card_type: str):
        """Updates the card type display (Instant / Sorcery / Creature)."""
        self.lbl_card_type.config(text=card_type)

    def finish(self):
        """Called when the program is done — disables buttons."""
        self.btn_next.config(text="Finished ✓", state="disabled", bg="#555")
        self.btn_auto.config(state="disabled", bg="#555")
        self.btn_pause.config(state="disabled")
        self.add_log("═" * 40)
        self.add_log("Program finished. No more cards in deck.")

    def enable_pause(self, on_pause_click):
        """Enables the pause button with a callback (called by Role 2 during auto play)."""
        self.btn_pause.config(state="normal", command=on_pause_click)

    def disable_pause(self):
        """Disables the pause button (called when auto play stops)."""
        self.btn_pause.config(state="disabled")


# ─────────────────────────────────────────────────────────────
# TEST BLOCK — runs without engine, uses mock data
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # Mock creature for testing
    class MockCreature:
        def __init__(self, name, p, t, counters=0):
            self.name     = name
            self.power    = p
            self.toughness = t
            self.counters = counters

    # Mock grid states to simulate game progression
    mock_states = [
        {
            "grid": [
                [MockCreature("Ooze", 2, 2, 0), None, MockCreature("Ooze", 2, 2, 1)],
                [MockCreature("Rotlung Reanimator", 2, 2, 0)]
            ],
            "card": "Slime Molding", "annot": "0,0", "log": "Slime Molding: Ooze placed at [0,0]"
        },
        {
            "grid": [
                [MockCreature("Ooze", 3, 3, 1), None, MockCreature("Ooze", 2, 2, 0)],
                [MockCreature("Rotlung Reanimator", 2, 2, 0)]
            ],
            "card": "Battlegrowth", "annot": "0,0", "log": "Battlegrowth: +1/+1 on [0,0]"
        },
        {
            "grid": [
                [MockCreature("Zombie", 2, 2, 0), None, MockCreature("Ooze", 3, 3, 1)],
                [MockCreature("Rotlung Reanimator", 2, 2, 0)]
            ],
            "card": "Infest", "annot": "", "log": "Infest: -2/-2 to all\n  Ooze dies → Rotlung triggers → Zombie created"
        },
    ]

    step = [0]

    def mock_next():
        if step[0] >= len(mock_states):
            app.finish()
            return
        s = mock_states[step[0]]
        app.update_board(s["grid"])
        app.set_card_played(s["card"], s["annot"])
        app.set_step(step[0] + 1, len(mock_states))
        app.add_log(s["log"])
        step[0] += 1

    def mock_auto():
        if step[0] < len(mock_states):
            mock_next()
            root.after(800, mock_auto)

    root = tk.Tk()
    app = MagicGUI(root, on_next_click=mock_next, on_auto_click=mock_auto)

    # Initial state
    app.add_log("Program loaded. Press 'Next Step' or 'Auto Play' to begin.")
    app.update_board([
        [MockCreature("Ooze", 2, 2, 0), None, MockCreature("Ooze", 2, 2, 1)],
        [MockCreature("Rotlung Reanimator", 2, 2, 0)]
    ])

    root.mainloop()
