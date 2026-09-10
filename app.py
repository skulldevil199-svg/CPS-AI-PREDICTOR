"""
app.py
------
Course Registration DBMS mini-project
GUI: Tkinter | Backend: MS Access via pyodbc

Roles:
  STUDENT -> can Add Course / Withdraw Course for themself, and view
             their own registrations + running credit total.
  FACULTY -> can Update a registration (reassign slot / faculty) and
             view every registration in the system.

Run order:
  1) setup_db.py   (once, to create the tables)
  2) app.py        (the actual application)
"""

import tkinter as tk
from tkinter import ttk, messagebox

import db


# ---------------------------------------------------------------------------
# LOGIN WINDOW
# ---------------------------------------------------------------------------
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Course Registration DBMS - Login")
        self.geometry("380x260")
        self.resizable(False, False)

        tk.Label(self, text="Course Registration System", font=("Segoe UI", 14, "bold")).pack(pady=(20, 5))
        tk.Label(self, text="MS Access backed | DBMS mini-project", font=("Segoe UI", 9)).pack(pady=(0, 15))

        self.role_var = tk.StringVar(value="STUDENT")
        role_frame = tk.Frame(self)
        role_frame.pack(pady=5)
        tk.Radiobutton(role_frame, text="Student", variable=self.role_var, value="STUDENT",
                       command=self._toggle_fields).pack(side="left", padx=10)
        tk.Radiobutton(role_frame, text="Faculty", variable=self.role_var, value="FACULTY",
                       command=self._toggle_fields).pack(side="left", padx=10)

        form = tk.Frame(self)
        form.pack(pady=10)

        self.id_label = tk.Label(form, text="Reg. No:")
        self.id_label.grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.id_entry = tk.Entry(form, width=22)
        self.id_entry.grid(row=0, column=1, pady=5)

        self.name_label = tk.Label(form, text="Name:")
        self.name_label.grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.name_entry = tk.Entry(form, width=22)
        self.name_entry.grid(row=1, column=1, pady=5)

        tk.Button(self, text="Continue", width=18, command=self._login).pack(pady=15)

    def _toggle_fields(self):
        if self.role_var.get() == "STUDENT":
            self.id_label.config(text="Reg. No:")
        else:
            self.id_label.config(text="Faculty ID:")

    def _login(self):
        ident = self.id_entry.get().strip()
        name = self.name_entry.get().strip()
        if not ident or not name:
            messagebox.showwarning("Missing info", "Please enter both fields.")
            return
        role = self.role_var.get()
        self.destroy()
        MainWindow(role, ident, name).mainloop()


# ---------------------------------------------------------------------------
# MAIN APPLICATION WINDOW
# ---------------------------------------------------------------------------
class MainWindow(tk.Tk):
    def __init__(self, role, ident, name):
        super().__init__()
        self.role = role          # "STUDENT" or "FACULTY"
        self.ident = ident        # RegNo or FacultyID
        self.name = name

        self.title(f"Course Registration DBMS - {role} ({ident})")
        self.geometry("760x520")

        header = tk.Label(
            self, text=f"Logged in as {role}: {name}  ({ident})",
            font=("Segoe UI", 11, "bold"), bg="#2c3e50", fg="white", pady=8
        )
        header.pack(fill="x")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        if role == "STUDENT":
            self.add_tab = AddCourseTab(notebook, self)
            self.withdraw_tab = WithdrawCourseTab(notebook, self)
            self.view_tab = ViewTab(notebook, self)
            notebook.add(self.add_tab, text="1. Add Course")
            notebook.add(self.withdraw_tab, text="2. Withdraw Course")
            notebook.add(self.view_tab, text="My Registrations")
        else:  # FACULTY
            self.update_tab = UpdateTab(notebook, self)
            self.view_tab = ViewTab(notebook, self)
            notebook.add(self.update_tab, text="3. Update Registration")
            notebook.add(self.view_tab, text="All Registrations")

        self.notebook = notebook
        self.view_tab.refresh()

    def refresh_all_views(self):
        self.view_tab.refresh()


# ---------------------------------------------------------------------------
# TAB 1: ADD COURSE  (Student)
# ---------------------------------------------------------------------------
class AddCourseTab(tk.Frame):
    def __init__(self, parent, app: MainWindow):
        super().__init__(parent, padx=20, pady=20)
        self.app = app

        fields = [
            ("Slot", "slot"),
            ("Subject", "subject"),
            ("Credits", "credits"),
            ("Faculty ID", "faculty_id"),
            ("Faculty Name", "faculty_name"),
        ]
        self.vars = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(self, text=label + ":", font=("Segoe UI", 10)).grid(row=i, column=0, sticky="e", pady=6, padx=5)
            e = tk.Entry(self, width=30)
            e.grid(row=i, column=1, pady=6)
            self.vars[key] = e

        tk.Button(self, text="Add Course", bg="#27ae60", fg="white", width=18,
                  command=self._submit).grid(row=len(fields), column=0, columnspan=2, pady=20)

    def _submit(self):
        try:
            slot = self.vars["slot"].get().strip()
            subject = self.vars["subject"].get().strip()
            credits_ = int(self.vars["credits"].get().strip())
            faculty_id = self.vars["faculty_id"].get().strip()
            faculty_name = self.vars["faculty_name"].get().strip()

            if not all([slot, subject, faculty_id, faculty_name]):
                raise ValueError("All fields are required.")

            db.add_course(
                reg_no=self.app.ident,
                name=self.app.name,
                slot=slot,
                subject=subject,
                credits_=credits_,
                faculty_id=faculty_id,
                faculty_name=faculty_name,
            )
            messagebox.showinfo("Success", f"Registered for '{subject}'.")
            for e in self.vars.values():
                e.delete(0, tk.END)
            self.app.refresh_all_views()

        except (ValueError, db.DBError) as e:
            messagebox.showerror("Could not add course", str(e))


# ---------------------------------------------------------------------------
# TAB 2: WITHDRAW COURSE  (Student)
# ---------------------------------------------------------------------------
class WithdrawCourseTab(tk.Frame):
    def __init__(self, parent, app: MainWindow):
        super().__init__(parent, padx=20, pady=20)
        self.app = app

        tk.Label(self, text="Subject to withdraw:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="e", pady=6, padx=5)
        self.subject_entry = tk.Entry(self, width=30)
        self.subject_entry.grid(row=0, column=1, pady=6)

        tk.Button(self, text="Withdraw Course", bg="#c0392b", fg="white", width=18,
                  command=self._submit).grid(row=1, column=0, columnspan=2, pady=20)

    def _submit(self):
        subject = self.subject_entry.get().strip()
        if not subject:
            messagebox.showwarning("Missing info", "Enter the subject name to withdraw.")
            return
        try:
            db.withdraw_course(self.app.ident, subject)
            messagebox.showinfo("Success", f"Withdrawn from '{subject}'.")
            self.subject_entry.delete(0, tk.END)
            self.app.refresh_all_views()
        except db.DBError as e:
            messagebox.showerror("Could not withdraw", str(e))


# ---------------------------------------------------------------------------
# TAB 3: UPDATE REGISTRATION  (Faculty)
# ---------------------------------------------------------------------------
class UpdateTab(tk.Frame):
    def __init__(self, parent, app: MainWindow):
        super().__init__(parent, padx=20, pady=20)
        self.app = app

        fields = [
            ("Student Reg. No", "reg_no"),
            ("Subject", "subject"),
            ("New Slot (optional)", "new_slot"),
            ("New Faculty ID (optional)", "new_faculty_id"),
            ("New Faculty Name (optional)", "new_faculty_name"),
        ]
        self.vars = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(self, text=label + ":", font=("Segoe UI", 10)).grid(row=i, column=0, sticky="e", pady=6, padx=5)
            e = tk.Entry(self, width=30)
            e.grid(row=i, column=1, pady=6)
            self.vars[key] = e

        tk.Button(self, text="Update Registration", bg="#2980b9", fg="white", width=20,
                  command=self._submit).grid(row=len(fields), column=0, columnspan=2, pady=20)

    def _submit(self):
        try:
            reg_no = self.vars["reg_no"].get().strip()
            subject = self.vars["subject"].get().strip()
            new_slot = self.vars["new_slot"].get().strip() or None
            new_fid = self.vars["new_faculty_id"].get().strip() or None
            new_fname = self.vars["new_faculty_name"].get().strip() or None

            if not reg_no or not subject:
                raise ValueError("Student Reg. No and Subject are required.")

            db.update_registration(reg_no, subject, new_slot, new_fid, new_fname)
            messagebox.showinfo("Success", f"Registration for {reg_no} / '{subject}' updated.")
            self.app.refresh_all_views()

        except (ValueError, db.DBError) as e:
            messagebox.showerror("Could not update", str(e))


# ---------------------------------------------------------------------------
# VIEW TAB (both roles) — shared registrations table + credit total
# ---------------------------------------------------------------------------
class ViewTab(tk.Frame):
    def __init__(self, parent, app: MainWindow):
        super().__init__(parent, padx=10, pady=10)
        self.app = app

        top = tk.Frame(self)
        top.pack(fill="x")
        tk.Button(top, text="Refresh", command=self.refresh).pack(side="left")
        self.credit_label = tk.Label(top, text="", font=("Segoe UI", 10, "bold"))
        self.credit_label.pack(side="right")

        cols = ("RegNo", "Name", "Slot", "Subject", "FacultyID", "FacultyName")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=110, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=10)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            if self.app.role == "STUDENT":
                rows = db.fetch_registrations(reg_no=self.app.ident)
                student = db.fetch_student(self.app.ident)
                total = student.TotalCredits if student else 0
                self.credit_label.config(text=f"Total credits: {total}")
            else:
                rows = db.fetch_registrations()
                self.credit_label.config(text="")

            for r in rows:
                self.tree.insert("", "end", values=(r.RegNo, r.Name, r.Slot, r.Subject, r.FacultyID, r.FacultyName))

        except db.DBError as e:
            messagebox.showerror("Database error", str(e))


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    LoginWindow().mainloop()
