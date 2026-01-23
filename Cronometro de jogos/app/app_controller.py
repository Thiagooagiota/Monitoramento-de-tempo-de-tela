import customtkinter as ctk
from datetime import datetime

# from home_view import HomeView
from foco_view import FocoView

class AppController:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.geometry("900x700+10+10")
        self.root.title("FocusDesk AI")
        ctk.set_appearance_mode("Dark")

        
        self.show_home()

    def show_home(self):
        self.home_view = FocoView(self.root, self)
        self.home_view.pack(fill="both", expand=True)


    def limpar_frame(self, frame):
            for widget in frame.winfo_children():
                widget.destroy()


    def run(self):
        self.root.mainloop() 
