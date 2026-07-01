from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from modules.base import BaseModuleFrame, COLORS, FONTS


class StudentsFrame(BaseModuleFrame):
    """Student management screen."""

    def __init__(self, parent: tk.Widget, app, db) -> None:
        super().__init__(parent, app, db)
        self.selected_student_id = None
        self.selected_student_has_account = False
        self.search_field_var = tk.StringVar(value="full_name")
        self.search_text_var = tk.StringVar()
        self.sort_column = "full_name"
        self.sort_ascending = True
        self._build_ui()
        self.refresh_data()

    def _build_ui(self) -> None:
        self.build_heading(
            "Student Management",
            "Add, edit, delete, and search student records. Student codes are generated automatically.",
        )

        self.build_search_bar(
            fields=["full_name", "student_code", "roll_no", "class_name"],
            field_var=self.search_field_var,
            text_var=self.search_text_var,
            on_search=self.load_data,
            on_reset=self._reset_search,
            default_field="full_name",
        )

        content = tk.Frame(self, bg=COLORS["bg"])
        content.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        left = tk.Frame(content, bg=COLORS["panel"], bd=0, highlightthickness=1, highlightbackground="#22314f")
        left.pack(side="left", fill="y", padx=(0, 12))
        left.configure(width=500)
        left.pack_propagate(False)

        form = tk.Frame(left, bg=COLORS["panel"], padx=10, pady=10)
        form.pack(fill="both", expand=True)

        self.student_code_entry = self.labeled_entry(form, "Student Code", 0, 0, readonly=True)
        self.full_name_entry = self.labeled_entry(form, "Full Name", 0, 1)
        self.class_name_entry = self.labeled_entry(form, "Class Name", 2, 0)
        self.section_entry = self.labeled_entry(form, "Section", 2, 1)
        self.roll_no_entry = self.labeled_entry(form, "Roll No", 4, 0)
        self.email_entry = self.labeled_entry(form, "Email", 4, 1)
        self.phone_entry = self.labeled_entry(form, "Phone", 6, 0)
        self.username_entry = self.labeled_entry(form, "Username", 6, 1)
        self.password_entry = self.labeled_entry(form, "Password", 8, 0, show="*")
        self.confirm_password_entry = self.labeled_entry(form, "Confirm Password", 8, 1, show="*")

        self.address_text = self.labeled_text(form, "Address", 10, 0, height=4)
        self.address_text.grid(columnspan=2)

        self.build_action_row(
            form,
            row=12,
            columnspan=2,
            actions=[
                ("Add", self.add_student, COLORS["success"]),
                ("Update", self.update_student, COLORS["warning"]),
                ("Delete", self.delete_student, COLORS["danger"]),
                ("Clear", self.clear_form, COLORS["secondary"]),
            ],
        )

        note = tk.Label(
            form,
            text=(
                "Username and password are optional. "
                "If a username is entered, a student login account will be created or updated."
            ),
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=FONTS["subtitle"],
            wraplength=430,
            justify="left",
        )
        note.grid(row=13, column=0, columnspan=2, sticky="w", padx=8, pady=(14, 0))

        right = tk.Frame(content, bg=COLORS["panel"], bd=0, highlightthickness=1, highlightbackground="#22314f")
        right.pack(side="right", fill="both", expand=True)

        table_wrap = tk.Frame(right, bg=COLORS["panel"], padx=10, pady=10)
        table_wrap.pack(fill="both", expand=True)

        columns = [
            "id",
            "student_code",
            "full_name",
            "class_name",
            "section",
            "roll_no",
            "email",
            "phone",
            "account_username",
            "join_date",
        ]
        self.tree = ttk.Treeview(table_wrap, columns=columns, show="headings", selectmode="browse")
        widths = {
            "id": 60,
            "student_code": 110,
            "full_name": 170,
            "class_name": 120,
            "section": 90,
            "roll_no": 100,
            "email": 170,
            "phone": 120,
            "account_username": 150,
            "join_date": 120,
        }
        self.configure_treeview(self.tree, columns, widths)
        for column in columns:
            self.tree.heading(column, text=column.replace("_", " ").title(), command=lambda c=column: self.sort_by(c))
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        form.columnconfigure(0, weight=1)
        form.columnconfigure(1, weight=1)

    def _reset_search(self) -> None:
        self.search_field_var.set("full_name")
        self.search_text_var.set("")
        self.load_data()

    def _set_student_code(self) -> None:
        code = self.db.generate_student_code()
        self.student_code_entry.configure(state="normal")
        self.student_code_entry.delete(0, tk.END)
        self.student_code_entry.insert(0, code)
        self.student_code_entry.configure(state="readonly")

    def clear_form(self) -> None:
        self.selected_student_id = None
        self.selected_student_has_account = False
        self.clear_entries(
            self.student_code_entry,
            self.full_name_entry,
            self.class_name_entry,
            self.section_entry,
            self.roll_no_entry,
            self.email_entry,
            self.phone_entry,
            self.username_entry,
            self.password_entry,
            self.confirm_password_entry,
            self.address_text,
        )
        self._set_student_code()
        self.tree.selection_remove(self.tree.selection())

    def _collect_student_data(self) -> dict:
        return {
            "student_code": self.student_code_entry.get().strip(),
            "full_name": self.full_name_entry.get().strip(),
            "class_name": self.class_name_entry.get().strip(),
            "section": self.section_entry.get().strip(),
            "roll_no": self.roll_no_entry.get().strip(),
            "email": self.email_entry.get().strip(),
            "phone": self.phone_entry.get().strip(),
            "address": self.address_text.get("1.0", tk.END).strip(),
        }

    def _collect_account_data(self) -> dict:
        return {
            "username": self.username_entry.get().strip(),
            "password": self.password_entry.get().strip(),
            "confirm_password": self.confirm_password_entry.get().strip(),
            "role": "student",
        }

    def _validate_student_data(self, data: dict) -> bool:
        required = ["full_name", "class_name", "roll_no", "address"]
        for field in required:
            if not data[field]:
                messagebox.showwarning("Validation Error", f"{field.replace('_', ' ').title()} is required.")
                return False
        return True

    def _build_account_payload(self, account_data: dict, is_update: bool = False) -> dict | None:
        username = account_data["username"]
        password = account_data["password"]
        confirm_password = account_data["confirm_password"]

        if not username and not password and not confirm_password:
            return None

        if not username:
            messagebox.showwarning("Validation Error", "Username is required when creating a student account.")
            return None

        if password != confirm_password:
            messagebox.showwarning("Validation Error", "Password confirmation does not match.")
            return None

        if not is_update and not password:
            messagebox.showwarning("Validation Error", "Password is required when creating a student account.")
            return None

        if is_update and not self.selected_student_has_account and not password:
            messagebox.showwarning("Validation Error", "Password is required when creating a new account for this student.")
            return None

        return {
            "username": username,
            "password": password,
            "role": "student",
        }

    def add_student(self) -> None:
        student_data = self._collect_student_data()
        account_data = self._collect_account_data()

        if not self._validate_student_data(student_data):
            return

        has_account_input = any(
        account_data[field]
        for field in ("username", "password", "confirm_password")
        )
        account = self._build_account_payload(account_data, is_update=False)
        if has_account_input and account is None:
            return

        try:
            self.db.add_student(student_data, account)
            messagebox.showinfo("Success", "Student added successfully.")
            self.clear_form()
            self.load_data()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def update_student(self) -> None:
        if self.selected_student_id is None:
            messagebox.showwarning("Selection Required", "Select a student to update.")
            return

        student_data = self._collect_student_data()
        account_data = self._collect_account_data()

        if not self._validate_student_data(student_data):
            return

        has_account_input = any(
        account_data[field]
        for field in ("username", "password", "confirm_password")
        )

        account = self._build_account_payload(account_data, is_update=True)
        if has_account_input and account is None:
            return

        try:
            self.db.update_student(self.selected_student_id, student_data, account)
            messagebox.showinfo("Success", "Student updated successfully.")
            self.load_data()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def delete_student(self) -> None:
        if self.selected_student_id is None:
            messagebox.showwarning("Selection Required", "Select a student to delete.")
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            "Delete the selected student? Any linked student login account will also be deleted.",
        ):
            return

        try:
            self.db.delete_student(self.selected_student_id)
            messagebox.showinfo("Success", "Student deleted successfully.")
            self.clear_form()
            self.load_data()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def load_data(self) -> None:
        students = self.db.fetch_students(
            self.search_text_var.get(),
            self.search_field_var.get(),
            self.sort_column,
            self.sort_ascending,
        )
        self.fill_treeview(
            self.tree,
            [
                (
                    student["id"],
                    student["student_code"],
                    student["full_name"],
                    student["class_name"],
                    student.get("section") or "",
                    student["roll_no"],
                    student.get("email") or "",
                    student.get("phone") or "",
                    student.get("account_username") or "",
                    student["join_date"],
                )
                for student in students
            ],
        )

    def refresh_data(self) -> None:
        self.load_data()
        self.clear_form()

    def sort_by(self, column: str) -> None:
        self.update_sort_state(column)
        self.load_data()

    def on_select(self, event) -> None:
        selection = self.tree.selection()
        if not selection:
            return

        values = self.tree.item(selection[0], "values")
        student = self.db.get_student_by_id(int(values[0]))
        if not student:
            return

        self.selected_student_id = student["id"]
        self.selected_student_has_account = bool(student.get("user_id"))

        self.clear_entries(
            self.student_code_entry,
            self.full_name_entry,
            self.class_name_entry,
            self.section_entry,
            self.roll_no_entry,
            self.email_entry,
            self.phone_entry,
            self.username_entry,
            self.password_entry,
            self.confirm_password_entry,
            self.address_text,
        )

        self.student_code_entry.configure(state="normal")
        self.student_code_entry.insert(0, student["student_code"])
        self.student_code_entry.configure(state="readonly")
        self.full_name_entry.insert(0, student["full_name"])
        self.class_name_entry.insert(0, student["class_name"])
        self.section_entry.insert(0, student.get("section") or "")
        self.roll_no_entry.insert(0, student["roll_no"])
        self.email_entry.insert(0, student.get("email") or "")
        self.phone_entry.insert(0, student.get("phone") or "")
        self.username_entry.insert(0, student.get("account_username") or "")
        self.address_text.insert("1.0", student["address"])
        