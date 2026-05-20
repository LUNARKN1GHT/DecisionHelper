import customtkinter as ctk
from ui.main_window import MainWindow

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
