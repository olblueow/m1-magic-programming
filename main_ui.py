import tkinter as tk
from gui import MagicGUI
from controller import GameController

# path to .cod
DECK_PATH = "data/test.cod"

# creating  controller
controller = GameController(DECK_PATH)
controller.load()


# ----------
# BUTTON: Next step
# ----------
def on_next():
    result = controller.next_step()

    # if error
    if result.get("error"):
        app.add_log(result["error"])
        return

    # if end
    if result.get("done"):
        app.update_board(result["board"])
        app.add_log("Program finished.")
        app.finish()
        return

    # update ui
    app.update_board(result["board"])
    app.set_card_played(result["card"], result["annotation"])
    app.set_step(result["step"] + 1, controller.get_total_steps())
    app.add_log(result["log"])
    print(result)


# ----------
# BUTTON: Auto play
# ----------
def on_auto():
    def loop():
        if controller.is_done():
            app.finish()
            return

        on_next()
        root.after(600, loop)  # for  tkinter

    loop()


# ----------
# Main
# ----------
root = tk.Tk()
app = MagicGUI(root, on_next_click=on_next, on_auto_click=on_auto)

# starting state
app.add_log("Program loaded. Press 'Next Step' or 'Auto Play'.")
app.update_board(controller.board.grid)
app.set_step(0, controller.get_total_steps())

root.mainloop()