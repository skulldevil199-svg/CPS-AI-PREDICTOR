"""
setup_db.py
-----------
Creates the 4 tables this project needs inside an EXISTING, EMPTY
Access database file called CourseDB.accdb (placed next to this script).

pyodbc/Access can run CREATE TABLE against a blank .accdb, but it cannot
create the .accdb file itself, so do this first:

  1. Open Microsoft Access
  2. File -> New -> Blank Database
  3. Name it exactly:  CourseDB.accdb
  4. Save it in the SAME folder as this script
  5. Close it (don't leave it open in Access while running this script)
  6. Run:  python setup_db.py

Re-running this script is safe — it skips any table that already exists.
"""

import os
import sys
import pyodbc

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CourseDB.accdb")

TABLES = {
    "Students": """
        CREATE TABLE Students (
            RegNo TEXT(20) PRIMARY KEY,
            Name TEXT(100),
            TotalCredits INTEGER
        )
    """,
    "Faculty": """
        CREATE TABLE Faculty (
            FacultyID TEXT(20) PRIMARY KEY,
            FacultyName TEXT(100)
        )
    """,
    "Subjects": """
        CREATE TABLE Subjects (
            SubjectName TEXT(100) PRIMARY KEY,
            Credits INTEGER
        )
    """,
    "Registrations": """
        CREATE TABLE Registrations (
            RegNo TEXT(20),
            Name TEXT(100),
            Slot TEXT(20),
            Subject TEXT(100),
            FacultyID TEXT(20),
            FacultyName TEXT(100),
            CONSTRAINT PK_Registration PRIMARY KEY (RegNo, Subject)
        )
    """,
}


def main():
    if not os.path.exists(DB_PATH):
        sys.exit(
            f"ERROR: {DB_PATH} does not exist.\n"
            "Create a blank Access database with that exact name/location first "
            "(see the instructions at the top of this file), then re-run this script."
        )

    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={DB_PATH};"
    )
    try:
        conn = pyodbc.connect(conn_str, autocommit=True)
    except pyodbc.Error as e:
        sys.exit(
            "ERROR: could not connect to CourseDB.accdb.\n"
            "Check that the Microsoft Access ODBC driver is installed and that "
            "the .accdb file isn't currently open in Access.\n\n"
            f"Details: {e}"
        )

    cur = conn.cursor()
    existing = {row.table_name for row in cur.tables(tableType="TABLE")}

    for name, ddl in TABLES.items():
        if name in existing:
            print(f"[skip]   {name} already exists")
            continue
        cur.execute(ddl)
        print(f"[created] {name}")

    conn.close()
    print("\nDone. CourseDB.accdb is ready for app.py")


if __name__ == "__main__":
    main()
