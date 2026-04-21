import tkinter as tk
import os
from PIL import Image, ImageTk, ImageDraw

# ─────────────────────────────────────────────────────────────
# COLOR SCHEME & THEME
# ─────────────────────────────────────────────────────────────
BG_MAIN      = "#111111"   
BG_PANEL     = "#1a1a1a"
BG_CANVAS    = "#1e1e1e"   
TEXT_MUTED   = "#7f8c8d"
TEXT_PRIMARY = "#ecf0f1"
TEXT_ACCENT  = "#f39c12"

class MagicGUI:
    def __init__(self, root, on_next_click, on_auto_click, on_pause_click, on_load_click):
        self.root = root
        self.root.title("Magic Programming")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG_MAIN)
        
        # Base card dimensions (100% zoom level)
        self.base_w = 100
        self.base_h = 140
        self.cell_w = self.base_w
        self.cell_h = self.base_h
        
        # Cache to prevent PIL images from being garbage collected
        self.image_cache = {} 
        
        # Ensure the images directory exists to prevent FileNotFoundError
        if not os.path.exists("images"):
            os.makedirs("images")

        self._build_layout(on_next_click, on_auto_click, on_pause_click, on_load_click)

    def _build_layout(self, on_next, on_auto, on_pause, on_load):
        # --- TOP HEADER: Controls and Info ---
        header = tk.Frame(self.root, bg=BG_PANEL, pady=10, padx=20)
        header.pack(fill="x")
        
        tk.Button(header, text="Load .cod Deck", command=on_load, bg="#000000", font=("Arial", 10, "bold")).pack(side="left")
        
        self.btn_next = tk.Button(header, text="Next Step", command=on_next, bg="#000000", font=("Arial", 10, "bold"))
        self.btn_next.pack(side="left", padx=10)
        
        self.btn_auto = tk.Button(header, text="Auto Play", command=on_auto, bg="#000000", font=("Arial", 10, "bold"))
        self.btn_auto.pack(side="left")

        self.btn_pause = tk.Button(header, text="Pause", command=on_pause, bg="#000000", font=("Arial", 10, "bold"), state="disabled")
        self.btn_pause.pack(side="left", padx=10)

        # Dynamic zoom slider (50% to 250%)
        self.scale_zoom = tk.Scale(header, from_=50, to=250, orient="horizontal", label="Zoom %", bg=BG_PANEL, fg=TEXT_PRIMARY, highlightthickness=0, command=self._on_zoom_change)
        self.scale_zoom.set(100)
        self.scale_zoom.pack(side="left", padx=20)
        
        # Step counter display
        self.lbl_step = tk.Label(header, text="Step 0 / -", bg=BG_PANEL, fg=TEXT_ACCENT, font=("Courier New", 12, "bold"))
        self.lbl_step.pack(side="right")

        # --- CENTER: Battlefield (Turing Band) ---
        bf_frame = tk.Frame(self.root, bg=BG_MAIN)
        bf_frame.pack(fill="both", expand=True, pady=10)
        
        tk.Label(bf_frame, text="THE BATTLEFIELD", bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 10, "bold")).pack()
        
        # Canvas with a vertical scrollbar for large memory tapes
        self.canvas_bf = tk.Canvas(bf_frame, bg=BG_CANVAS, highlightthickness=2, highlightbackground="#333")
        self.scrollbar_bf = tk.Scrollbar(bf_frame, orient="vertical", command=self.canvas_bf.yview)
        self.canvas_bf.configure(yscrollcommand=self.scrollbar_bf.set)

        self.scrollbar_bf.pack(side="right", fill="y")
        self.canvas_bf.pack(side="left", fill="both", expand=True, padx=20, pady=5)
        
        # Bind resize event to automatically wrap cards to the next line
        self.canvas_bf.bind("<Configure>", lambda e: self._on_canvas_resize())

        # --- BOTTOM: Playmat (Stack, Log, Graveyard, Deck) ---
        playmat = tk.Frame(self.root, bg="#000000", height=200)
        playmat.pack(fill="x", side="bottom")
        
        # 1. The Stack (where current card is shown)
        stack_frame = tk.Frame(playmat, bg="#000000", width=200, pady=10)
        stack_frame.pack(side="left", padx=20)
        tk.Label(stack_frame, text="THE STACK", bg="#000000", fg=TEXT_ACCENT, font=("Arial", 10, "bold")).pack()
        self.canvas_stack = tk.Canvas(stack_frame, width=120, height=168, bg="#111", highlightthickness=0)
        self.canvas_stack.pack()

        # 2. Battle Log (history of engine events)
        log_frame = tk.Frame(playmat, bg="#000000", pady=10)
        log_frame.pack(side="left", fill="both", expand=True, padx=10)
        tk.Label(log_frame, text="BATTLE LOG", bg="#000000", fg=TEXT_MUTED, font=("Arial", 10, "bold")).pack()
        self.log_text = tk.Text(log_frame, height=8, bg="#111", fg="#a9cce3", font=("Courier New", 10), state="disabled")
        self.log_text.pack(fill="both", expand=True)

        # 3. Graveyard & Deck (Right panel)
        gd_frame = tk.Frame(playmat, bg="#000000", pady=10)
        gd_frame.pack(side="right", padx=20)
        
        # Graveyard (discard pile)
        grave_box = tk.Frame(gd_frame, bg="#000000")
        grave_box.pack(side="left", padx=10)
        tk.Label(grave_box, text="GRAVEYARD", bg="#000000", fg=TEXT_MUTED, font=("Arial", 10, "bold")).pack()
        self.canvas_grave = tk.Canvas(grave_box, width=100, height=140, bg="#222", highlightthickness=1, highlightbackground="#444")
        self.canvas_grave.pack()
        
        # Deck (remaining instructions)
        deck_box = tk.Frame(gd_frame, bg="#000000")
        deck_box.pack(side="left", padx=10)
        tk.Label(deck_box, text="DECK", bg="#000000", fg=TEXT_MUTED, font=("Arial", 10, "bold")).pack()
        
        self.canvas_deck = tk.Canvas(deck_box, width=100, height=140, bg="#2c3e50", highlightthickness=1, highlightbackground="#34495e")
        self.canvas_deck.pack()
        
        # Draw the physical deck back once
        self._draw_deck_back()
        
        # Create the dynamic text element to show remaining cards
        self.lbl_cards_left = self.canvas_deck.create_text(50, 110, text="", fill="white", font=("Arial", 10, "bold")) 

        # Holds the active grid data to redraw properly on window resize
        self.current_grid = None

    def _on_zoom_change(self, val):
        """Adjusts the cell size based on the slider value and triggers a board redraw."""
        scale = int(val) / 100.0
        self.cell_w = int(self.base_w * scale)
        self.cell_h = int(self.base_h * scale)
        if self.current_grid is not None:
            self.update_board(self.current_grid)

    def set_auto_mode(self, is_playing):
        """Toggles button states to prevent conflicting commands during Auto Play."""
        if is_playing:
            self.btn_next.config(state="disabled")
            self.btn_auto.config(state="disabled")
            self.btn_pause.config(state="normal")
        else:
            self.btn_next.config(state="normal")
            self.btn_auto.config(state="normal")
            self.btn_pause.config(state="disabled")

    def _get_card_image(self, card_name, width, height):
        """Loads the image from the /images folder or generates a colored placeholder."""
        cache_key = f"{card_name}_{width}x{height}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        img_path = None
        for ext in [".png", ".jpg", ".jpeg"]:
            if os.path.exists(f"images/{card_name}{ext}"):
                img_path = f"images/{card_name}{ext}"
                break

        if img_path:
            img = Image.open(img_path).resize((width, height), Image.Resampling.LANCZOS)
        else:
            # Fallback placeholder generation if no image file is found
            colors = {"Ooze": "#27ae60", "Zombie": "#2c3e50", "Rotlung Reanimator": "#8e44ad"}
            color = colors.get(card_name, "#34495e")
            img = Image.new('RGB', (width, height), color=color)
            draw = ImageDraw.Draw(img)
            draw.rectangle([5, 5, width-5, height-5], outline="white", width=2)

        photo = ImageTk.PhotoImage(img)
        self.image_cache[cache_key] = photo
        return photo

    def reset_playmat(self, total_steps):
        """Clears all dynamic elements on the GUI when a new deck is loaded."""
        self.set_step(0, total_steps)
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, "end")
        self.log_text.config(state="disabled")
        self.canvas_grave.delete("all")
        self.canvas_stack.delete("all")
        self.current_grid = None
        
        self.btn_next.config(state="normal", text="Next Step")
        self.btn_auto.config(state="normal", text="Auto Play")
        self.btn_pause.config(state="disabled")

    def show_in_stack(self, card_name, annotation):
        """Displays the currently played card in the Stack area."""
        self.canvas_stack.delete("all")
        img = self._get_card_image(card_name, 120, 168)
        self.canvas_stack.create_image(60, 84, image=img)
        self.canvas_stack.create_text(60, 150, text=card_name, fill="white", font=("Arial", 9, "bold"))
        if annotation:
            self.canvas_stack.create_text(60, 15, text=annotation, fill="#f39c12", font=("Courier", 8, "bold"))

    def move_stack_to_graveyard(self, card_name):
        """Moves the resolved card from the Stack to the Graveyard visually."""
        self.canvas_stack.delete("all")
        img = self._get_card_image(card_name, 100, 140)
        self.canvas_grave.create_image(50, 70, image=img)
        self.canvas_grave.create_text(50, 70, text=card_name, fill="white", font=("Arial", 8, "bold"))

    def _draw_deck_back(self):
        """Draws the static back of a Magic card in the Deck area."""
        self.canvas_deck.create_rectangle(5, 5, 95, 135, fill="#8e44ad", outline="#f39c12", width=3)
        self.canvas_deck.create_text(50, 60, text="MAGIC\nDeck", fill="#f39c12", font=("Georgia", 10, "bold"), justify="center")

    def _on_canvas_resize(self):
        """Triggers a board redraw to adjust card wrapping when window is resized."""
        if self.current_grid is not None:
            self.update_board(self.current_grid)

    def update_board(self, grid_dict):
        """Parses the sparse matrix grid and triggers drawing for both memory rows."""
        self.current_grid = grid_dict
        self.canvas_bf.delete("all")
        if not grid_dict: return

        # Extract items by row (0 = Memory, 1 = CPU) and retain real column indices
        row0_items = [(col, grid_dict[(r, col)]) for r, col in grid_dict.keys() if r == 0]
        row1_items = [(col, grid_dict[(r, col)]) for r, col in grid_dict.keys() if r == 1]
        
        # Sort items by their column index (from lowest negative to highest positive)
        row0_items.sort(key=lambda x: x[0])
        row1_items.sort(key=lambda x: x[0])

        next_y = 20
        next_y = self._draw_row(row0_items, next_y, "ROW 0: MEMORY TAPE")
        next_y += 30 # Gap between rows
        self._draw_row(row1_items, next_y, "ROW 1: PROCESSOR")

        # Update the scrollable area bounds based on where the drawing stopped
        self.canvas_bf.configure(scrollregion=self.canvas_bf.bbox("all"))

    def _draw_row(self, row_items, start_y, row_name):
        """Draws a logical row of cards, wrapping them to a new line if they exceed canvas width."""
        self.canvas_bf.create_text(20, start_y + 10, text=row_name, fill=TEXT_MUTED, font=("Courier New", 10, "bold"), anchor="w")
        
        if not row_items: 
            return start_y + 30

        canvas_w = self.canvas_bf.winfo_width()
        if canvas_w < 100: canvas_w = 1000 # Fallback width upon initialization

        current_x = 20
        current_y = start_y + 40

        for col, creature in row_items:
            if not creature: continue
            
            # Line wrap logic: If card exceeds right border, move it to the line below
            if current_x + self.cell_w + 10 > canvas_w:
                current_x = 20
                current_y += self.cell_h + 40 

            x_center = current_x + (self.cell_w // 2)
            y_center = current_y + (self.cell_h // 2)

            name = creature.name if hasattr(creature, 'name') else str(creature)
            img = self._get_card_image(name, self.cell_w, self.cell_h)
            
            # Draw the actual card image
            self.canvas_bf.create_image(x_center, y_center, image=img)
            
            # Overlay Power/Toughness stats and highlight the Read/Write Head
            if hasattr(creature, 'power') and hasattr(creature, 'toughness'):
                stats = f"{creature.power}/{creature.toughness}"
                
                # The 'Head' of the Turing Machine is strictly the 2/2 creature
                is_head = (creature.power == 2 and creature.toughness == 2)
                bg_color = "#c0392b" if is_head else "#2980b9" # Red for Head, Blue for standard
                
                # Dynamic scaling for the stats box based on zoom level
                scale_ratio = self.cell_w / 100.0
                box_w = max(30, int(30 * scale_ratio))
                box_h = max(20, int(20 * scale_ratio))
                
                box_x2 = x_center + (self.cell_w // 2) - max(2, int(5 * scale_ratio))
                box_y2 = y_center + (self.cell_h // 2) - max(2, int(5 * scale_ratio))
                box_x1 = box_x2 - box_w
                box_y1 = box_y2 - box_h
                
                font_size = max(6, int(10 * scale_ratio))
                
                self.canvas_bf.create_rectangle(box_x1, box_y1, box_x2, box_y2, fill=bg_color, outline="white")
                self.canvas_bf.create_text((box_x1 + box_x2) / 2, (box_y1 + box_y2) / 2, text=stats, fill="white", font=("Arial", font_size, "bold"))

            # Display the real logical index column below the card
            self.canvas_bf.create_text(x_center, current_y - 15, text=f"[{col}]", fill=TEXT_MUTED, font=("Courier New", 9))

            # Move cursor right for the next card
            current_x += self.cell_w + 15

        # Returns the lowest Y coordinate reached to properly space the next row
        return current_y + self.cell_h

    def add_log(self, message):
        """Safely appends a message to the read-only log text widget."""
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"> {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def set_step(self, current, total):
        """Updates the step counter label and the Deck card count."""
        self.lbl_step.config(text=f"Step {current} / {total}")
        
        cards_left = total - current
        self.canvas_deck.itemconfig(self.lbl_cards_left, text=f"{cards_left} left")

    def finish(self):
        """Locks the controls and signals the end of the simulation."""
        self.btn_next.config(state="disabled", text="Finished")
        self.btn_auto.config(state="disabled")
        self.btn_pause.config(state="disabled")
        self.add_log("=== PROGRAM TERMINATED ===")