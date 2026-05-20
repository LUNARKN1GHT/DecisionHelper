import customtkinter as ctk
from models import Decision


class MatrixView(ctk.CTkToplevel):
    def __init__(self, parent, decision: Decision, on_save=None):
        super().__init__(parent)
        self.title(decision.title)
        self.geometry("600x400")
        ctk.CTkLabel(self, text="矩阵评分界面（即将实现）").pack(expand=True)
