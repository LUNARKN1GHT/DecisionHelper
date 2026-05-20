import customtkinter as ctk
from tkinter import simpledialog, messagebox
from models import Decision
import storage


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("DecisionHelper")
        self.geometry("480x560")
        self.resizable(False, False)

        self.decisions: list[Decision] = storage.load_decisions()
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 标题
        ctk.CTkLabel(self, text="我的决策", font=ctk.CTkFont(size=22, weight="bold")).grid(
            row=0, column=0, pady=(24, 8)
        )

        # 决策列表
        self.listbox = ctk.CTkScrollableFrame(self)
        self.listbox.grid(row=1, column=0, sticky="nsew", padx=24, pady=8)
        self.listbox.grid_columnconfigure(0, weight=1)

        # 底部按钮
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=16, padx=24, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(btn_frame, text="＋ 新建决策", command=self._new_decision).grid(
            row=0, column=0, padx=(0, 8), sticky="ew"
        )
        ctk.CTkButton(
            btn_frame, text="删除选中", fg_color="#e05252", hover_color="#b83c3c",
            command=self._delete_decision
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

        self._selected: int | None = None

    def _refresh_list(self):
        for widget in self.listbox.winfo_children():
            widget.destroy()
        self._selected = None

        if not self.decisions:
            ctk.CTkLabel(self.listbox, text="暂无决策，点击「新建决策」开始", text_color="gray").grid(
                row=0, column=0, pady=40
            )
            return

        for i, decision in enumerate(self.decisions):
            row = ctk.CTkFrame(self.listbox, cursor="hand2")
            row.grid(row=i, column=0, sticky="ew", pady=4)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(row, text=decision.title, font=ctk.CTkFont(size=15), anchor="w").grid(
                row=0, column=0, sticky="ew", padx=16, pady=10
            )
            ctk.CTkLabel(
                row, text=decision.created_at[:10], font=ctk.CTkFont(size=11),
                text_color="gray", anchor="e"
            ).grid(row=0, column=1, padx=16)

            row.bind("<Button-1>", lambda e, idx=i: self._select(idx))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, idx=i: self._select(idx))
            row.bind("<Double-Button-1>", lambda e, idx=i: self._open(idx))
            for child in row.winfo_children():
                child.bind("<Double-Button-1>", lambda e, idx=i: self._open(idx))

            self._rows = getattr(self, "_rows", [])

        self._rows = [self.listbox.winfo_children()[i] for i in range(len(self.decisions))]

    def _select(self, idx: int):
        if self._selected is not None and self._selected < len(self._rows):
            self._rows[self._selected].configure(fg_color=["gray86", "gray17"])
        self._selected = idx
        self._rows[idx].configure(fg_color=["#c9d9f0", "#2a3f5f"])

    def _open(self, idx: int):
        from ui.matrix_view import MatrixView
        MatrixView(self, self.decisions[idx], on_save=self._on_save)

    def _new_decision(self):
        title = simpledialog.askstring("新建决策", "决策标题：", parent=self)
        if not title or not title.strip():
            return
        decision = Decision(title=title.strip())
        self.decisions.append(decision)
        storage.save_decisions(self.decisions)
        self._refresh_list()

    def _delete_decision(self):
        if self._selected is None:
            messagebox.showinfo("提示", "请先选择一条决策", parent=self)
            return
        title = self.decisions[self._selected].title
        if not messagebox.askyesno("确认删除", f'确定删除「{title}」吗？', parent=self):
            return
        self.decisions.pop(self._selected)
        storage.save_decisions(self.decisions)
        self._refresh_list()

    def _on_save(self):
        storage.save_decisions(self.decisions)
        self._refresh_list()
