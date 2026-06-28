from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Iterable, Sequence


COLORS = {
    "bg": "#0f172a",
    "panel": "#111c33",
    "panel_alt": "#172554",
    "card": "#1e293b",
    "primary": "#2563eb",
    "primary_dark": "#1d4ed8",
    "secondary": "#334155",
    "accent": "#38bdf8",
    "success": "#16a34a",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "text": "#f8fafc",
    "muted": "#cbd5e1",
    "entry_bg": "#f8fafc",
    "table_bg": "#ffffff",
}

FONTS = {
    "title": ("Segoe UI", 18, "bold"),
    "subtitle": ("Segoe UI", 10),
    "heading": ("Segoe UI", 14, "bold"),
    "body": ("Segoe UI", 10),
    "button": ("Segoe UI", 10, "bold"),
    "card_value": ("Segoe UI", 22, "bold"),
    "card_label": ("Segoe UI", 10, "bold"),
}


class BaseModuleFrame(tk.Frame):
    """Common scaffolding for application module screens."""

    def __init__(self, parent: tk.Widget, app, db) -> None:
        super().__init__(parent, bg=COLORS["bg"])
        self.app = app
        self.db = db
        self.selected_id = None
        self._sort_column = None
        self._sort_ascending = True

    def build_heading(self, title: str, subtitle: str = "") -> tk.Frame:
        container = tk.Frame(self, bg=COLORS["bg"])
        container.pack(fill="x", padx=24, pady=(18, 12))

        title_label = tk.Label(
            container,
            text=title,
            bg=COLORS["bg"],
            fg=COLORS["text"],
            font=FONTS["title"],
        )
        title_label.pack(anchor="w")

        if subtitle:
            subtitle_label = tk.Label(
                container,
                text=subtitle,
                bg=COLORS["bg"],
                fg=COLORS["muted"],
                font=FONTS["subtitle"],
            )
            subtitle_label.pack(anchor="w", pady=(4, 0))

        return container

    def build_card(self, parent: tk.Widget, title: str, value: str, accent: str) -> tk.Frame:
        card = tk.Frame(parent, bg=COLORS["card"], bd=0, highlightthickness=1, highlightbackground="#22314f")
        card.pack_propagate(False)

        accent_bar = tk.Frame(card, bg=accent, height=4)
        accent_bar.pack(fill="x", side="top")

        title_label = tk.Label(
            card,
            text=title,
            bg=COLORS["card"],
            fg=COLORS["muted"],
            font=FONTS["card_label"],
        )
        title_label.pack(anchor="w", padx=16, pady=(16, 6))

        value_label = tk.Label(
            card,
            text=value,
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=FONTS["card_value"],
        )
        value_label.pack(anchor="w", padx=16, pady=(0, 16))
        return card
    
    def build_search_bar(
        self,
        fields: Sequence[str],
        field_var: tk.StringVar,
        text_var: tk.StringVar,
        on_search: Callable[[], None],
        on_reset: Callable[[], None],
        default_field: str | None = None,
    ) -> tk.Frame:
        search_bar = tk.Frame(self, bg=COLORS["panel"], padx=18, pady=14)
        search_bar.pack(fill="x", padx=24, pady=(0, 16))

        if default_field is not None:
            field_var.set(default_field)

        tk.Label(
            search_bar,
            text="Search By",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=FONTS["body"],
        ).grid(row=0, column=0, sticky="w", padx=6)

        search_field = ttk.Combobox(
            search_bar,
            textvariable=field_var,
            values=list(fields),
            state="readonly",
            width=16,
        )
        search_field.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(
            search_bar,
            text="Keyword",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=FONTS["body"],
        ).grid(row=0, column=2, sticky="w", padx=6)

        search_entry = tk.Entry(
            search_bar,
            textvariable=text_var,
            width=28,
            relief="flat",
        )
        search_entry.grid(row=0, column=3, padx=6, pady=6)

        tk.Button(
            search_bar,
            text="Search",
            command=on_search,
            bg=COLORS["primary"],
            fg="white",
            activebackground=COLORS["primary_dark"],
            relief="flat",
            font=FONTS["button"],
        ).grid(row=0, column=4, padx=6)

        tk.Button(
            search_bar,
            text="Reset",
            command=on_reset,
            bg=COLORS["secondary"],
            fg="white",
            activebackground="#475569",
            relief="flat",
            font=FONTS["button"],
        ).grid(row=0, column=5, padx=6)

        search_bar.columnconfigure(6, weight=1)
        self.search_field = search_field
        self.search_entry = search_entry

        return search_bar

    def build_action_row(
        self,
        parent: tk.Widget,
        row: int,
        actions: Sequence[tuple[str, Callable[[], None], str]],
        column: int = 0,
        columnspan: int = 1,
    ) -> tk.Frame:
        action_row = tk.Frame(parent, bg=COLORS["panel"])
        action_row.grid(
            row=row,
            column=column,
            columnspan=columnspan,
            sticky="ew",
            padx=8,
            pady=(12, 0),
        )

        action_row.columnconfigure(tuple(range(len(actions))), weight=1)

        for index, (text, command, color) in enumerate(actions):
            tk.Button(
                action_row,
                text=text,
                command=command,
                bg=color,
                fg="white",
                activebackground=color,
                relief="flat",
                font=FONTS["button"],
            ).grid(row=0, column=index, sticky="ew", padx=3)

        return action_row

    def update_sort_state(self, column: str) -> None:
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True

    def labeled_entry(
        self,
        parent: tk.Widget,
        label_text: str,
        row: int,
        column: int,
        width: int = 28,
        show: str | None = None,
        readonly: bool = False,
    ) -> tk.Entry:
        label = tk.Label(
            parent,
            text=label_text,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=FONTS["body"],
        )
        label.grid(row=row, column=column, sticky="w", padx=8, pady=(8, 3))

        entry = tk.Entry(
            parent,
            width=width,
            show=show,
            relief="flat",
            bg=COLORS["entry_bg"],
            fg="#0f172a",
            insertbackground="#0f172a",
            font=FONTS["body"],
        )
        entry.grid(row=row + 1, column=column, sticky="ew", padx=8, pady=(0, 8))
        if readonly:
            entry.configure(state="readonly")
        return entry

    def labeled_text(self, parent: tk.Widget, label_text: str, row: int, column: int, height: int = 4) -> tk.Text:
        label = tk.Label(
            parent,
            text=label_text,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=FONTS["body"],
        )
        label.grid(row=row, column=column, sticky="w", padx=8, pady=(8, 3))

        text = tk.Text(
            parent,
            height=height,
            relief="flat",
            bg=COLORS["entry_bg"],
            fg="#0f172a",
            insertbackground="#0f172a",
            font=FONTS["body"],
            wrap="word",
        )
        text.grid(row=row + 1, column=column, sticky="ew", padx=8, pady=(0, 8))
        return text

    def configure_treeview(self, tree: ttk.Treeview, columns: Sequence[str], widths: dict[str, int] | None = None) -> None:
        widths = widths or {}
        tree["columns"] = columns
        tree["show"] = "headings"
        for column in columns:
            tree.heading(column, text=column.replace("_", " ").title())
            tree.column(column, width=widths.get(column, 130), anchor="center", stretch=True)

    def fill_treeview(self, tree: ttk.Treeview, rows: Iterable[Sequence[object]]) -> None:
        for item in tree.get_children():
            tree.delete(item)
        for row in rows:
            tree.insert("", "end", values=row)

    def clear_entries(self, *widgets) -> None:
        for widget in widgets:
            if isinstance(widget, tk.Entry):
                state = str(widget.cget("state"))
                if state == "readonly":
                    widget.configure(state="normal")
                    widget.delete(0, tk.END)
                    widget.configure(state="readonly")
                else:
                    widget.delete(0, tk.END)
            elif isinstance(widget, tk.Text):
                widget.delete("1.0", tk.END)
            elif isinstance(widget, tk.StringVar):
                widget.set("")

    def set_sort(self, column: str) -> None:
        if self._sort_column == column:
            self._sort_ascending = not self._sort_ascending
        else:
            self._sort_column = column
            self._sort_ascending = True
