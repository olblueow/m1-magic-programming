import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk, ImageDraw

# COLOR SCHEME & THEME
BG_MAIN      = "#111111"   
BG_PANEL     = "#1a1a1a"
BG_CANVAS    = "#1e1e1e"   
TEXT_MUTED   = "#7f8c8d"
TEXT_PRIMARY = "#ecf0f1"
TEXT_ACCENT  = "#f39c12"

class MagicGUI:
    def __init__(self, root, on_next_click, on_auto_click, on_pause_click, on_load_click, on_compile_click):
        self.root = root
        self.root.title("MTG Turing IDE")
        self.root.geometry("1200x850")
        self.root.configure(bg=BG_MAIN)
        
        self.base_w = 100
        self.base_h = 140
        self.cell_w = self.base_w
        self.cell_h = self.base_h
        
        self.image_cache = {} 
        self.raw_var_map = {}
        self.variable_map = {} 
        
        if not os.path.exists("images"):
            os.makedirs("images")

        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=BG_MAIN, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG_PANEL, foreground=TEXT_PRIMARY, padding=[15, 5], font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#2980b9")])

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tab_editor = tk.Frame(self.notebook, bg=BG_MAIN)
        self.tab_visualizer = tk.Frame(self.notebook, bg=BG_MAIN)

        self.notebook.add(self.tab_editor, text=" 1. CODE EDITOR ")
        self.notebook.add(self.tab_visualizer, text=" 2. VISUALIZER ")

        self._build_editor_layout(on_compile_click)
        self._build_visualizer_layout(on_next_click, on_auto_click, on_pause_click, on_load_click)

    def _build_editor_layout(self, on_compile):
        toolbar = tk.Frame(self.tab_editor, bg=BG_PANEL, pady=10, padx=20)
        toolbar.pack(fill="x")
        
        tk.Label(toolbar, text="High-Level Python Source Code", bg=BG_PANEL, fg=TEXT_ACCENT, font=("Arial", 12, "bold")).pack(side="left")
        
        btn_compile = tk.Button(toolbar, text="COMPILE AND RUN", command=on_compile)
        btn_compile.pack(side="right")

        editor_frame = tk.Frame(self.tab_editor, bg=BG_MAIN, padx=20, pady=10)
        editor_frame.pack(fill="both", expand=True)

        self.text_editor = tk.Text(editor_frame, bg="#1e1e1e", fg="#ecf0f1", font=("Courier New", 14), insertbackground="white", padx=10, pady=10)
        self.text_editor.pack(fill="both", expand=True)
        
        default_code = "x = 5\ny = 2\n\nx += 1\ny += 5\ny -= 2\nx *= 2\nx = 1 * 2\n"
        self.text_editor.insert("1.0", default_code)

        console_frame = tk.Frame(self.tab_editor, bg="#000000", height=150)
        console_frame.pack(fill="x", side="bottom")
        tk.Label(console_frame, text="COMPILER OUTPUT", bg="#000000", fg=TEXT_MUTED, font=("Arial", 10, "bold"), anchor="w").pack(fill="x", padx=10, pady=5)
        
        self.compiler_console = tk.Text(console_frame, height=6, bg="#050505", fg="#2ecc71", font=("Courier New", 10), state="disabled")
        self.compiler_console.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def get_editor_code(self):
        return self.text_editor.get("1.0", tk.END)

    def set_compiler_status(self, message, is_error=False):
        self.compiler_console.config(state="normal")
        self.compiler_console.delete("1.0", tk.END)
        color = "#e74c3c" if is_error else "#2ecc71"
        self.compiler_console.configure(fg=color)
        self.compiler_console.insert("end", f"> {message}\n")
        self.compiler_console.config(state="disabled")

    def switch_to_visualizer(self):
        self.notebook.select(self.tab_visualizer)
        
    def set_variable_map(self, var_map):
        """Stores the variable mapping from the compiler to decode binary values."""
        self.raw_var_map = var_map
        self.variable_map = {}
        for var_name, cols in var_map.items():
            for c in cols:
                self.variable_map[c] = var_name

        if not var_map:
            self.lbl_variables.config(text="No variables mapped.\nCompile to inspect.")

    def _build_visualizer_layout(self, on_next, on_auto, on_pause, on_load):
        header = tk.Frame(self.tab_visualizer, bg=BG_PANEL, pady=10, padx=20)
        header.pack(fill="x")
        
        tk.Button(header, text="Load .cod Deck", command=on_load).pack(side="left")
        self.btn_next = tk.Button(header, text="Next Step", command=on_next)
        self.btn_next.pack(side="left", padx=10)
        self.btn_auto = tk.Button(header, text="Auto Play", command=on_auto)
        self.btn_auto.pack(side="left")
        self.btn_pause = tk.Button(header, text="Pause", command=on_pause, state="disabled")
        self.btn_pause.pack(side="left", padx=10)
        
        self.scale_speed = tk.Scale(header, from_=200, to=2000, orient="horizontal", label="Delay (ms)", bg=BG_PANEL, fg=TEXT_PRIMARY, highlightthickness=0)
        self.scale_speed.set(800)
        self.scale_speed.pack(side="left", padx=10)

        self.scale_zoom = tk.Scale(header, from_=50, to=250, orient="horizontal", label="Zoom %", bg=BG_PANEL, fg=TEXT_PRIMARY, highlightthickness=0, command=self._on_zoom_change)
        self.scale_zoom.set(100)
        self.scale_zoom.pack(side="left", padx=10)
        
        self.lbl_step = tk.Label(header, text="Step 0 / -", bg=BG_PANEL, fg=TEXT_ACCENT, font=("Courier New", 12, "bold"))
        self.lbl_step.pack(side="right")

        # Central container for Battlefield and Memory Inspector
        bf_container = tk.Frame(self.tab_visualizer, bg=BG_MAIN)
        bf_container.pack(fill="both", expand=True, pady=10)

        # Left side: Battlefield Canvas
        bf_frame = tk.Frame(bf_container, bg=BG_MAIN)
        bf_frame.pack(side="left", fill="both", expand=True)
        tk.Label(bf_frame, text="THE BATTLEFIELD", bg=BG_MAIN, fg=TEXT_MUTED, font=("Arial", 10, "bold")).pack()
        
        self.canvas_bf = tk.Canvas(bf_frame, bg=BG_CANVAS, highlightthickness=2, highlightbackground="#333")
        self.scrollbar_bf = tk.Scrollbar(bf_frame, orient="vertical", command=self.canvas_bf.yview)
        self.canvas_bf.configure(yscrollcommand=self.scrollbar_bf.set)

        self.scrollbar_bf.pack(side="right", fill="y")
        self.canvas_bf.pack(side="left", fill="both", expand=True, padx=20, pady=5)
        self.canvas_bf.bind("<Configure>", lambda e: self._on_canvas_resize())

        # Right side: Memory Inspector Panel
        inspector_frame = tk.Frame(bf_container, bg=BG_PANEL, width=250)
        inspector_frame.pack(side="right", fill="y", padx=(0, 20), pady=5)
        tk.Label(inspector_frame, text="MEMORY INSPECTOR", bg=BG_PANEL, fg=TEXT_ACCENT, font=("Arial", 10, "bold")).pack(pady=10)
        
        self.lbl_variables = tk.Label(inspector_frame, text="Compile code to\ninspect variables.", bg=BG_PANEL, fg=TEXT_PRIMARY, font=("Courier New", 14, "bold"), justify="left")
        self.lbl_variables.pack(padx=20, pady=10, anchor="nw")

        # Bottom: Playmat
        playmat = tk.Frame(self.tab_visualizer, bg="#000000", height=200)
        playmat.pack(fill="x", side="bottom")
        
        stack_frame = tk.Frame(playmat, bg="#000000", width=200, pady=10)
        stack_frame.pack(side="left", padx=20)
        tk.Label(stack_frame, text="THE STACK", bg="#000000", fg=TEXT_ACCENT, font=("Arial", 10, "bold")).pack()
        self.canvas_stack = tk.Canvas(stack_frame, width=120, height=168, bg="#111", highlightthickness=0)
        self.canvas_stack.pack()

        log_frame = tk.Frame(playmat, bg="#000000", pady=10)
        log_frame.pack(side="left", fill="both", expand=True, padx=10)
        tk.Label(log_frame, text="BATTLE LOG", bg="#000000", fg=TEXT_MUTED, font=("Arial", 10, "bold")).pack()
        self.log_text = tk.Text(log_frame, height=8, bg="#111", fg="#a9cce3", font=("Courier New", 10), state="disabled")
        self.log_text.pack(fill="both", expand=True)

        gd_frame = tk.Frame(playmat, bg="#000000", pady=10)
        gd_frame.pack(side="right", padx=20)
        
        grave_box = tk.Frame(gd_frame, bg="#000000")
        grave_box.pack(side="left", padx=10)
        tk.Label(grave_box, text="GRAVEYARD", bg="#000000", fg=TEXT_MUTED, font=("Arial", 10, "bold")).pack()
        self.canvas_grave = tk.Canvas(grave_box, width=100, height=140, bg="#222", highlightthickness=1, highlightbackground="#444")
        self.canvas_grave.pack()
        
        deck_box = tk.Frame(gd_frame, bg="#000000")
        deck_box.pack(side="left", padx=10)
        tk.Label(deck_box, text="DECK", bg="#000000", fg=TEXT_MUTED, font=("Arial", 10, "bold")).pack()
        
        self.canvas_deck = tk.Canvas(deck_box, width=100, height=140, bg="#2c3e50", highlightthickness=1, highlightbackground="#34495e")
        self.canvas_deck.pack()
        
        self._draw_deck_back()
        self.lbl_cards_left = self.canvas_deck.create_text(50, 110, text="", fill="white", font=("Arial", 10, "bold")) 
        self.current_grid = None

    def get_delay(self):
        return int(self.scale_speed.get())

    def _on_zoom_change(self, val):
        scale = int(val) / 100.0
        self.cell_w = int(self.base_w * scale)
        self.cell_h = int(self.base_h * scale)
        if self.current_grid is not None:
            self.update_board(self.current_grid)

    def set_auto_mode(self, is_playing):
        if is_playing:
            self.btn_next.config(state="disabled")
            self.btn_auto.config(state="disabled")
            self.btn_pause.config(state="normal")
        else:
            self.btn_next.config(state="normal")
            self.btn_auto.config(state="normal")
            self.btn_pause.config(state="disabled")

    def _get_card_image(self, card_name, width, height):
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
            colors = {"Ooze": "#27ae60", "Zombie": "#2c3e50", "Rotlung Reanimator": "#8e44ad"}
            color = colors.get(card_name, "#34495e")
            img = Image.new('RGB', (width, height), color=color)
            draw = ImageDraw.Draw(img)
            draw.rectangle([5, 5, width-5, height-5], outline="white", width=2)

        photo = ImageTk.PhotoImage(img)
        self.image_cache[cache_key] = photo
        return photo

    def reset_playmat(self, total_steps):
        self.set_step(0, total_steps)
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, "end")
        self.log_text.config(state="disabled")
        self.canvas_grave.delete("all")
        self.canvas_stack.delete("all")
        self.current_grid = None
        
        self.btn_next.config(state="normal")
        self.btn_auto.config(state="normal")
        self.btn_pause.config(state="disabled")

    def show_in_stack(self, card_name, annotation):
        self.canvas_stack.delete("all")
        img = self._get_card_image(card_name, 120, 168)
        self.canvas_stack.create_image(60, 84, image=img)
        self.canvas_stack.create_text(60, 150, text=card_name, fill="white", font=("Arial", 9, "bold"))
        if annotation:
            self.canvas_stack.create_text(60, 15, text=annotation, fill="#f39c12", font=("Courier", 8, "bold"))

    def move_stack_to_graveyard(self, card_name):
        self.canvas_stack.delete("all")
        img = self._get_card_image(card_name, 100, 140)
        self.canvas_grave.create_image(50, 70, image=img)
        self.canvas_grave.create_text(50, 70, text=card_name, fill="white", font=("Arial", 8, "bold"))

    def _draw_deck_back(self):
        self.canvas_deck.create_rectangle(5, 5, 95, 135, fill="#8e44ad", outline="#f39c12", width=3)
        self.canvas_deck.create_text(50, 60, text="MAGIC\nDeck", fill="#f39c12", font=("Georgia", 10, "bold"), justify="center")

    def _on_canvas_resize(self):
        if self.current_grid is not None:
            self.update_board(self.current_grid)

    def update_board(self, grid_dict):
        self.current_grid = grid_dict
        self.canvas_bf.delete("all")
        if not grid_dict: return

        row0_items = [(col, grid_dict[(r, col)]) for r, col in grid_dict.keys() if r == 0]
        row1_items = [(col, grid_dict[(r, col)]) for r, col in grid_dict.keys() if r == 1]
        
        row0_items.sort(key=lambda x: x[0])
        row1_items.sort(key=lambda x: x[0])

        next_y = 20
        next_y = self._draw_row(row0_items, next_y, "ROW 0: MEMORY TAPE")
        # Ensure there is a gap between the memory row and the processor row
        next_y += 30 
        self._draw_row(row1_items, next_y, "ROW 1: PROCESSOR")

        self.canvas_bf.configure(scrollregion=self.canvas_bf.bbox("all"))
        self._update_inspector(grid_dict)

    def _update_inspector(self, grid_dict):
        """Reads the Memory Tape to update the Memory Inspector with decimal values."""
        if not self.raw_var_map:
            return
            
        inspector_text = ""
        for var_name, cols in self.raw_var_map.items():
            binary_str = ""
            for col in cols:
                card = grid_dict.get((0, col)) 
                if card is not None and card.name == "Zombie":
                    binary_str += "1"
                else:
                    binary_str += "0" 
            try:
                decimal_val = int(binary_str, 2)
                inspector_text += f"{var_name} = {decimal_val}\n[{binary_str}]\n\n"
            except ValueError:
                pass
                
        self.lbl_variables.config(text=inspector_text)

    def _draw_row(self, row_items, start_y, row_name):
        self.canvas_bf.create_text(20, start_y + 10, text=row_name, fill=TEXT_MUTED, font=("Courier New", 10, "bold"), anchor="w")
        
        if not row_items: 
            return start_y + 40

        canvas_w = self.canvas_bf.winfo_width()
        if canvas_w < 100: canvas_w = 1000 

        current_x = 20
        # Increased Y padding so variables text does not overlap with row titles
        current_y = start_y + 70

        for col, creature in row_items:
            if not creature: continue
            
            if current_x + self.cell_w + 10 > canvas_w:
                current_x = 20
                # Slightly larger wrap spacing to prevent overlaps on new lines
                current_y += self.cell_h + 60 

            x_center = current_x + (self.cell_w // 2)
            y_center = current_y + (self.cell_h // 2)

            name = creature.name if hasattr(creature, 'name') else str(creature)
            img = self._get_card_image(name, self.cell_w, self.cell_h)
            
            self.canvas_bf.create_image(x_center, y_center, image=img)
            
            if hasattr(creature, 'power') and hasattr(creature, 'toughness'):
                stats = f"{creature.power}/{creature.toughness}"
                is_head = (creature.power == 2 and creature.toughness == 2)
                bg_color = "#c0392b" if is_head else "#2980b9"
                
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

            # Display Variable Name Above the card
            var_name = self.variable_map.get(col, "")
            label_text = f"[{col}]\n{var_name}" if var_name and "MEMORY" in row_name else f"[{col}]"
            label_color = TEXT_ACCENT if var_name else TEXT_MUTED
            
            # Adjusted Y offset (-30) to create breathing room from the card's top edge
            self.canvas_bf.create_text(x_center, current_y - 30, text=label_text, fill=label_color, font=("Courier New", 9, "bold"), justify="center")

            current_x += self.cell_w + 15

        # Return Y position offset for the next row
        return current_y + self.cell_h + 20

    def add_log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"> {message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def set_step(self, current, total):
        self.lbl_step.config(text=f"Step {current} / {total}")
        cards_left = total - current
        self.canvas_deck.itemconfig(self.lbl_cards_left, text=f"{cards_left} left")

    def finish(self):
        self.btn_next.config(state="disabled")
        self.btn_auto.config(state="disabled")
        self.btn_pause.config(state="disabled")
        self.add_log("=== PROGRAM TERMINATED ===")