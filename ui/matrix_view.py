import customtkinter as ctk
from tkinter import simpledialog, messagebox
from models import Decision, Criterion, Score


class MatrixView(ctk.CTkToplevel):
    def __init__(self, parent, decision: Decision, on_save=None):
        super().__init__(parent)
        self.decision = decision
        self.on_save = on_save
        self.title(decision.title)
        self.geometry("760x620")
        self.resizable(True, True)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_management()
        self._build_matrix()
        self._build_results()

    # ── 标题 ──────────────────────────────────────────────
    def _build_header(self):
        ctk.CTkLabel(
            self, text=self.decision.title,
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, pady=(20, 4))

    # ── 选项 / 标准管理 ───────────────────────────────────
    def _build_management(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=24, pady=8)
        frame.grid_columnconfigure((0, 1), weight=1)

        self._build_options_panel(frame)
        self._build_criteria_panel(frame)

    def _build_options_panel(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="选项", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, pady=(10, 4)
        )

        self.options_list = ctk.CTkScrollableFrame(frame, height=100)
        self.options_list.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8)
        self.options_list.grid_columnconfigure(0, weight=1)

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=2, pady=8, padx=8, sticky="ew")
        btn_row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_row, text="＋ 添加", width=80, command=self._add_option).grid(
            row=0, column=0, padx=(0, 4), sticky="ew"
        )
        ctk.CTkButton(
            btn_row, text="删除", width=80, fg_color="#e05252", hover_color="#b83c3c",
            command=self._delete_option
        ).grid(row=0, column=1, padx=(4, 0), sticky="ew")

        self._selected_option: str | None = None
        self._refresh_options()

    def _build_criteria_panel(self, parent):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="标准", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, columnspan=2, pady=(10, 4)
        )

        self.criteria_list = ctk.CTkScrollableFrame(frame, height=100)
        self.criteria_list.grid(row=1, column=0, columnspan=2, sticky="ew", padx=8)
        self.criteria_list.grid_columnconfigure(0, weight=1)

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.grid(row=2, column=0, columnspan=2, pady=8, padx=8, sticky="ew")
        btn_row.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(btn_row, text="＋ 添加", width=80, command=self._add_criterion).grid(
            row=0, column=0, padx=(0, 4), sticky="ew"
        )
        ctk.CTkButton(
            btn_row, text="删除", width=80, fg_color="#e05252", hover_color="#b83c3c",
            command=self._delete_criterion
        ).grid(row=0, column=1, padx=(4, 0), sticky="ew")

        self._selected_criterion: str | None = None
        self._refresh_criteria()

    # ── 矩阵表格 ──────────────────────────────────────────
    def _build_matrix(self):
        self.matrix_outer = ctk.CTkScrollableFrame(self)
        self.matrix_outer.grid(row=2, column=0, sticky="nsew", padx=24, pady=4)
        self._refresh_matrix()

    def _refresh_matrix(self):
        for w in self.matrix_outer.winfo_children():
            w.destroy()
        self._score_vars: dict[tuple[str, str], ctk.StringVar] = {}

        criteria = self.decision.criteria
        options = self.decision.options

        if not criteria and not options:
            ctk.CTkLabel(self.matrix_outer, text="请先添加选项和标准", text_color="gray").grid(pady=20)
            return

        # 表头
        ctk.CTkLabel(self.matrix_outer, text="", width=120).grid(row=0, column=0, padx=4, pady=4)
        for j, c in enumerate(criteria):
            ctk.CTkLabel(
                self.matrix_outer,
                text=f"{c.name}\n(权重 {c.weight})",
                font=ctk.CTkFont(size=12),
                width=90, wraplength=85, justify="center"
            ).grid(row=0, column=j + 1, padx=4, pady=4)

        # 每行
        existing: dict[tuple[str, str], int] = {
            (s.option, s.criterion_id): s.value for s in self.decision.scores
        }
        for i, opt in enumerate(options):
            ctk.CTkLabel(
                self.matrix_outer, text=opt, anchor="w", width=120
            ).grid(row=i + 1, column=0, padx=4, pady=4, sticky="w")

            for j, c in enumerate(criteria):
                var = ctk.StringVar(value=str(existing.get((opt, c.id), "")))
                self._score_vars[(opt, c.id)] = var
                entry = ctk.CTkEntry(
                    self.matrix_outer, textvariable=var, width=60, justify="center"
                )
                entry.grid(row=i + 1, column=j + 1, padx=4, pady=4)
                var.trace_add("write", lambda *_, o=opt, cid=c.id: self._on_score_change(o, cid))

    # ── 结果排名 ──────────────────────────────────────────
    def _build_results(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(4, 16))
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text="排名结果", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, pady=(10, 4)
        )
        self.results_label = ctk.CTkLabel(frame, text="—", text_color="gray")
        self.results_label.grid(row=1, column=0, pady=(0, 10))
        self._refresh_results()

    def _refresh_results(self):
        ranked = self.decision.ranked_options()
        if not ranked or all(score is None for _, score in ranked):
            self.results_label.configure(text="填写评分后显示结果")
            return
        lines = []
        for rank, (opt, score) in enumerate(ranked, 1):
            score_str = f"{score:.2f}" if score is not None else "—"
            lines.append(f"#{rank}  {opt}  {score_str}")
        self.results_label.configure(text="    ".join(lines))

    # ── 数据操作 ──────────────────────────────────────────
    def _add_option(self):
        name = simpledialog.askstring("添加选项", "选项名称：", parent=self)
        if not name or not name.strip():
            return
        name = name.strip()
        if name in self.decision.options:
            messagebox.showwarning("重复", f"选项「{name}」已存在", parent=self)
            return
        self.decision.options.append(name)
        self._save()
        self._refresh_options()
        self._refresh_matrix()
        self._refresh_results()

    def _delete_option(self):
        if not self._selected_option:
            messagebox.showinfo("提示", "请先选择一个选项", parent=self)
            return
        opt = self._selected_option
        self.decision.options.remove(opt)
        self.decision.scores = [s for s in self.decision.scores if s.option != opt]
        self._selected_option = None
        self._save()
        self._refresh_options()
        self._refresh_matrix()
        self._refresh_results()

    def _add_criterion(self):
        name = simpledialog.askstring("添加标准", "标准名称：", parent=self)
        if not name or not name.strip():
            return
        weight_str = simpledialog.askstring("权重", "权重（1–3）：", parent=self)
        try:
            weight = int(weight_str)
            assert 1 <= weight <= 3
        except (TypeError, ValueError, AssertionError):
            messagebox.showerror("错误", "权重须为 1、2 或 3", parent=self)
            return
        self.decision.criteria.append(Criterion(name=name.strip(), weight=weight))
        self._save()
        self._refresh_criteria()
        self._refresh_matrix()
        self._refresh_results()

    def _delete_criterion(self):
        if not self._selected_criterion:
            messagebox.showinfo("提示", "请先选择一个标准", parent=self)
            return
        cid = self._selected_criterion
        self.decision.criteria = [c for c in self.decision.criteria if c.id != cid]
        self.decision.scores = [s for s in self.decision.scores if s.criterion_id != cid]
        self._selected_criterion = None
        self._save()
        self._refresh_criteria()
        self._refresh_matrix()
        self._refresh_results()

    def _on_score_change(self, option: str, criterion_id: str):
        var = self._score_vars.get((option, criterion_id))
        if var is None:
            return
        try:
            value = int(var.get())
            assert 1 <= value <= 5
        except (ValueError, AssertionError):
            return
        self.decision.scores = [
            s for s in self.decision.scores
            if not (s.option == option and s.criterion_id == criterion_id)
        ]
        self.decision.scores.append(Score(option=option, criterion_id=criterion_id, value=value))
        self._save()
        self._refresh_results()

    def _save(self):
        if self.on_save:
            self.on_save()

    # ── 列表刷新 ──────────────────────────────────────────
    def _refresh_options(self):
        for w in self.options_list.winfo_children():
            w.destroy()
        for opt in self.decision.options:
            row = ctk.CTkFrame(self.options_list, cursor="hand2")
            row.grid(sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=1)
            lbl = ctk.CTkLabel(row, text=opt, anchor="w")
            lbl.grid(row=0, column=0, sticky="ew", padx=8, pady=4)
            for w in (row, lbl):
                w.bind("<Button-1>", lambda e, o=opt: self._select_option(o))

    def _refresh_criteria(self):
        for w in self.criteria_list.winfo_children():
            w.destroy()
        for c in self.decision.criteria:
            row = ctk.CTkFrame(self.criteria_list, cursor="hand2")
            row.grid(sticky="ew", pady=2)
            row.grid_columnconfigure(0, weight=1)
            lbl = ctk.CTkLabel(row, text=f"{c.name}  ×{c.weight}", anchor="w")
            lbl.grid(row=0, column=0, sticky="ew", padx=8, pady=4)
            for w in (row, lbl):
                w.bind("<Button-1>", lambda e, cid=c.id: self._select_criterion(cid))

    def _select_option(self, opt: str):
        self._selected_option = opt
        for row in self.options_list.winfo_children():
            lbl = row.winfo_children()[0] if row.winfo_children() else None
            if lbl:
                is_sel = lbl.cget("text") == opt
                row.configure(fg_color=["#c9d9f0", "#2a3f5f"] if is_sel else ["gray86", "gray17"])

    def _select_criterion(self, cid: str):
        self._selected_criterion = cid
        cmap = {c.id: c.name for c in self.decision.criteria}
        for row in self.criteria_list.winfo_children():
            lbl = row.winfo_children()[0] if row.winfo_children() else None
            if lbl:
                name = lbl.cget("text").split("  ×")[0]
                matched_cid = next((k for k, v in cmap.items() if v == name), None)
                is_sel = matched_cid == cid
                row.configure(fg_color=["#c9d9f0", "#2a3f5f"] if is_sel else ["gray86", "gray17"])
