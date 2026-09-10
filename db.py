"""
db.py
-----
All MS Access connectivity and CRUD logic for the Course Registration DBMS
mini-project. Uses pyodbc + the Microsoft Access ODBC driver.

Schema (created by setup_db.py):

    Students(RegNo PK, Name, TotalCredits)
    Faculty(FacultyID PK, FacultyName)
    Subjects(SubjectName PK, Credits)
    Registrations(RegNo, Name, Slot, Subject, FacultyID, FacultyName)
        -- composite key (RegNo, Subject)

The "accurate credit" requirement from the spec is handled here:
every Add/Withdraw runs inside a single transaction so a student's
TotalCredits always stays in sync with their active registrations.
"""

import os
import pyodbc

# ---------------------------------------------------------------------------
# CONFIG - point this at your .accdb file
# ---------------------------------------------------------------------------
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CourseDB.accdb")

CONN_STR = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    rf"DBQ={DB_PATH};"
)


class DBError(Exception):
    """Raised for any expected/handled database problem (shown to the user)."""
    pass


def get_connection():
    try:
        return pyodbc.connect(CONN_STR, autocommit=False)
    except pyodbc.Error as e:
        raise DBError(
            "Could not connect to the Access database.\n"
            f"Expected file at:\n{DB_PATH}\n\n"
            "Make sure:\n"
            "  1) CourseDB.accdb exists (run setup_db.py first)\n"
            "  2) The 'Microsoft Access Driver (*.mdb, *.accdb)' is installed\n"
            "     (on 64-bit Python you need the 64-bit Access driver / "
            "     Access Database Engine redistributable)\n\n"
            f"Original error: {e}"
        )


# ---------------------------------------------------------------------------
# LOOKUP HELPERS
# ---------------------------------------------------------------------------
def get_student(conn, reg_no):
    cur = conn.cursor()
    cur.execute("SELECT RegNo, Name, TotalCredits FROM Students WHERE RegNo=?", reg_no)
    return cur.fetchone()


def get_faculty(conn, faculty_id):
    cur = conn.cursor()
    cur.execute("SELECT FacultyID, FacultyName FROM Faculty WHERE FacultyID=?", faculty_id)
    return cur.fetchone()


def get_subject(conn, subject_name):
    cur = conn.cursor()
    cur.execute("SELECT SubjectName, Credits FROM Subjects WHERE SubjectName=?", subject_name)
    return cur.fetchone()


def get_registration(conn, reg_no, subject_name):
    cur = conn.cursor()
    cur.execute(
        "SELECT RegNo, Name, Slot, Subject, FacultyID, FacultyName "
        "FROM Registrations WHERE RegNo=? AND Subject=?",
        reg_no, subject_name,
    )
    return cur.fetchone()


def list_registrations(conn, reg_no=None):
    cur = conn.cursor()
    if reg_no:
        cur.execute(
            "SELECT RegNo, Name, Slot, Subject, FacultyID, FacultyName "
            "FROM Registrations WHERE RegNo=? ORDER BY Subject", reg_no
        )
    else:
        cur.execute(
            "SELECT RegNo, Name, Slot, Subject, FacultyID, FacultyName "
            "FROM Registrations ORDER BY RegNo, Subject"
        )
    return cur.fetchall()


# ---------------------------------------------------------------------------
# ENSURE-EXISTS HELPERS (auto-create master rows the first time we see them)
# ---------------------------------------------------------------------------
def ensure_student(conn, reg_no, name):
    cur = conn.cursor()
    if get_student(conn, reg_no) is None:
        cur.execute(
            "INSERT INTO Students (RegNo, Name, TotalCredits) VALUES (?, ?, 0)",
            reg_no, name,
        )


def ensure_faculty(conn, faculty_id, faculty_name):
    cur = conn.cursor()
    if get_faculty(conn, faculty_id) is None:
        cur.execute(
            "INSERT INTO Faculty (FacultyID, FacultyName) VALUES (?, ?)",
            faculty_id, faculty_name,
        )


def ensure_subject(conn, subject_name, credits_):
    cur = conn.cursor()
    if get_subject(conn, subject_name) is None:
        cur.execute(
            "INSERT INTO Subjects (SubjectName, Credits) VALUES (?, ?)",
            subject_name, credits_,
        )


# ---------------------------------------------------------------------------
# 1. ADD COURSE
# ---------------------------------------------------------------------------
def add_course(reg_no, name, slot, subject, credits_, faculty_id, faculty_name):
    """
    Registers a student for a subject and increases their TotalCredits
    by that subject's credit value. Whole operation is one transaction.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        if get_registration(conn, reg_no, subject) is not None:
            raise DBError(f"{reg_no} is already registered for '{subject}'.")

        ensure_student(conn, reg_no, name)
        ensure_faculty(conn, faculty_id, faculty_name)
        ensure_subject(conn, subject, credits_)

        cur.execute(
            "INSERT INTO Registrations (RegNo, Name, Slot, Subject, FacultyID, FacultyName) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            reg_no, name, slot, subject, faculty_id, faculty_name,
        )

        cur.execute(
            "UPDATE Students SET TotalCredits = TotalCredits + ? WHERE RegNo=?",
            credits_, reg_no,
        )

        conn.commit()
    except pyodbc.Error as e:
        conn.rollback()
        raise DBError(f"Add course failed, no changes were made.\n{e}")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 2. WITHDRAW COURSE
# ---------------------------------------------------------------------------
def withdraw_course(reg_no, subject):
    """
    Removes a registration and reduces the student's TotalCredits by that
    subject's credit value (never below zero). One transaction.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        reg_row = get_registration(conn, reg_no, subject)
        if reg_row is None:
            raise DBError(f"No registration found for {reg_no} in '{subject}'.")

        subj_row = get_subject(conn, subject)
        credits_ = subj_row.Credits if subj_row else 0

        cur.execute(
            "DELETE FROM Registrations WHERE RegNo=? AND Subject=?",
            reg_no, subject,
        )
        cur.execute(
            "UPDATE Students SET TotalCredits = IIF(TotalCredits - ? < 0, 0, TotalCredits - ?) "
            "WHERE RegNo=?",
            credits_, credits_, reg_no,
        )

        conn.commit()
    except pyodbc.Error as e:
        conn.rollback()
        raise DBError(f"Withdraw failed, no changes were made.\n{e}")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 3. UPDATE REGISTRATION  (slot / faculty reassignment)
# ---------------------------------------------------------------------------
def update_registration(reg_no, subject, new_slot=None, new_faculty_id=None, new_faculty_name=None):
    conn = get_connection()
    try:
        cur = conn.cursor()

        if get_registration(conn, reg_no, subject) is None:
            raise DBError(f"No registration found for {reg_no} in '{subject}'.")

        if new_faculty_id and new_faculty_name:
            ensure_faculty(conn, new_faculty_id, new_faculty_name)

        sets, params = [], []
        if new_slot:
            sets.append("Slot=?")
            params.append(new_slot)
        if new_faculty_id:
            sets.append("FacultyID=?")
            params.append(new_faculty_id)
        if new_faculty_name:
            sets.append("FacultyName=?")
            params.append(new_faculty_name)

        if not sets:
            raise DBError("Nothing to update — provide a new slot and/or faculty.")

        params += [reg_no, subject]
        cur.execute(
            f"UPDATE Registrations SET {', '.join(sets)} WHERE RegNo=? AND Subject=?",
            *params,
        )

        conn.commit()
    except pyodbc.Error as e:
        conn.rollback()
        raise DBError(f"Update failed, no changes were made.\n{e}")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# READ-ONLY convenience wrappers (open + close their own connection)
# ---------------------------------------------------------------------------
def fetch_student(reg_no):
    conn = get_connection()
    try:
        return get_student(conn, reg_no)
    finally:
        conn.close()


def fetch_registrations(reg_no=None):
    conn = get_connection()
    try:
        return list_registrations(conn, reg_no)
    finally:
        conn.close()
