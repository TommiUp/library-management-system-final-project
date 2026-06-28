from __future__ import annotations

import csv
import tkinter as tk
from typing import Any, Callable
from tkinter import filedialog, messagebox, ttk

from modules.base import BaseModuleFrame, COLORS, FONTS


REPORT_COLUMNS = {
    "Available Books": [
        "book_code",
        "title",
        "author",
        "category",
        "publisher",
        "isbn",
        "quantity",
        "available_quantity",
        "shelf_location",
        "added_date",
    ],
    "Issued Books": [
        "id",
        "book_code",
        "title",
        "member_code",
        "member_name",
        "issue_date",
        "due_date",
        "return_date",
        "status",
        "fine_amount",
    ],
    "Overdue Books": [
        "id",
        "book_code",
        "title",
        "member_code",
        "member_name",
        "issue_date",
        "due_date",
        "status",
        "fine_amount",
    ],
    "Member Report": [
        "member_code",
        "name",
        "email",
        "phone",
        "address",
        "join_date",
    ],
    "Fine Report": [
        "id",
        "book_code",
        "title",
        "member_code",
        "member_name",
        "issue_date",
        "due_date",
        "return_date",
        "status",
        "fine_amount",
    ],
}

MONEY_COLUMNS = {"fine_amount"}


class ReportsFrame(BaseModuleFrame):
    """Reporting and export screen."""

    def __init__(self, parent: tk.Widget, app, db) -> None:
        super().__init__(parent, app, db)
        self.report_var = tk.StringVar(value="Available Books")
        self.current_columns = []
        self.current_rows = []
        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        self.build_heading(
            "Reports",
            "Generate availability, issue, overdue, member, and fine reports. Export any report to CSV.",
        )

        controls = tk.Frame(self, bg=COLORS["panel"], padx=18, pady=14)
        controls.pack(fill="x", padx=24, pady=(0, 16))

        tk.Label(controls, text="Report Type", bg=COLORS["panel"], fg=COLORS["text"], font=FONTS["body"]).grid(
            row=0, column=0, sticky="w", padx=6
        )
        self.report_combo = ttk.Combobox(
            controls,
            textvariable=self.report_var,
            values=list(REPORT_COLUMNS.keys()),
            state="readonly",
            width=22,
        )
        self.report_combo.grid(row=0, column=1, padx=6)

        tk.Button(
            controls,
            text="Load Report",
            command=self.load_report,
            bg=COLORS["primary"],
            fg="white",
            relief="flat",
            font=FONTS["button"],
        ).grid(row=0, column=2, padx=6)

        tk.Button(
            controls,
            text="Export CSV",
            command=self.export_csv,
            bg=COLORS["success"],
            fg="white",
            relief="flat",
            font=FONTS["button"],
        ).grid(row=0, column=3, padx=6)

        self.summary_label = tk.Label(
            controls,
            text="0 records",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=FONTS["body"],
        )
        self.summary_label.grid(row=0, column=4, padx=12, sticky="e")
        controls.columnconfigure(4, weight=1)

        table_frame = tk.Frame(self, bg=COLORS["panel"], bd=0, highlightthickness=1, highlightbackground="#22314f")
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        inner = tk.Frame(table_frame, bg=COLORS["panel"], padx=10, pady=10)
        inner.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(inner, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(inner, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def _report_loaders(self) -> dict[str, Callable[[], list[dict[str, Any]]]]:
        return {
            "Available Books": self.db.report_available_books,
            "Issued Books": self.db.report_issued_books,
            "Overdue Books": self.db.report_overdue_books,
            "Member Report": self.db.report_members,
            "Fine Report": self.db.report_fines,
        }

    def _format_cell(self, column: str, value: Any) -> Any:
        if value is None:
            return ""
        if column in MONEY_COLUMNS:
            return f"Tk {float(value):.2f}"
        return value

    def _format_row(self, row: dict[str, Any]) -> tuple[Any, ...]:
        return tuple(
            self._format_cell(column, row.get(column))
            for column in self.current_columns
        )

    def _configure_tree(self, columns: list[str]) -> None:
        self.tree["columns"] = columns
        for item in self.tree.get_children():
            self.tree.delete(item)
        for column in columns:
            self.tree.heading(column, text=column.replace("_", " ").title())
            self.tree.column(column, width=140, anchor="center", stretch=True)

    def load_report(self) -> None:
        report_name = self.report_var.get()
        self.current_columns = REPORT_COLUMNS[report_name]
        loader = self._report_loaders()[report_name]
        rows = loader()
        self.current_rows = [self._format_row(row) for row in rows]
        self._configure_tree(self.current_columns)
        for row in self.current_rows:
            self.tree.insert("", "end", values=row)
        self.summary_label.configure(text=f"{len(self.current_rows)} records")

    def refresh_data(self) -> None:
        self.load_report()

    def export_csv(self) -> None:
        if not self.current_rows:
            messagebox.showwarning("No Data", "Load a report before exporting.")
            return
        report_name = self.report_var.get().lower().replace(" ", "_")
        file_path = filedialog.asksaveasfilename(
            title="Export report to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"{report_name}.csv",
        )
        if not file_path:
            return
        try:
            with open(file_path, "w", newline="", encoding="utf-8") as file_handle:
                writer = csv.writer(file_handle)
                writer.writerow(self.current_columns)
                writer.writerows(self.current_rows)
            messagebox.showinfo("Export Complete", f"Report exported to {file_path}")
        except Exception as exc:
            messagebox.showerror("Export Failed", str(exc))
