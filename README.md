# Course Registration DBMS Mini-Project

Python (Tkinter) front end connected to **MS Access** via `pyodbc`, covering:

- Student Reg.No / Name, Slot, Subject, Faculty ID / Name (as one registration record)
- **Add Course**, **Withdraw Course**, **Update Registration** (the 3 operations from the spec)
- Two roles: **Student** (Add/Withdraw their own courses, view their credit total)
  and **Faculty** (Update slot/faculty assignments, view all registrations)
- "Accurate credit" requirement: every Add/Withdraw updates the student's
  `TotalCredits` inside the same transaction, so it can never drift out of sync

## Requirements

- Windows, with **Microsoft Access** (or just the free
  [Access Database Engine redistributable](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
  if you don't have full Access installed)
- Python 3.9+
- `pip install pyodbc`

> Match bitness: if you installed 64-bit Python, you need the 64-bit Access
> driver/engine (and vice versa for 32-bit).

## Setup (do this once)

1. Open Microsoft Access → **File → New → Blank Database**
2. Name it exactly **`CourseDB.accdb`**
3. Save it in the **same folder** as `app.py` / `setup_db.py`
4. **Close it** in Access (don't leave the file open while running the scripts)
5. From that folder, run:
   ```
   python setup_db.py
   ```
   This creates the 4 tables: `Students`, `Faculty`, `Subjects`, `Registrations`.

## Running the app

```
python app.py
```

- Choose **Student** and enter your Reg. No + Name to add/withdraw courses.
- Choose **Faculty** and enter your Faculty ID + Name to update registrations
  (reassign slot or faculty) and view every student's registrations.

## Files

| File | Purpose |
|---|---|
| `setup_db.py` | One-time script that creates the Access tables |
| `db.py` | All SQL / pyodbc logic (Add, Withdraw, Update, lookups) |
| `app.py` | Tkinter GUI — login screen + role-based tabs |

## Notes / possible extensions

- Currently `Subjects.Credits` is entered by the student on first Add — in a
  stricter version, an admin/faculty screen could pre-populate the subject
  catalog instead of trusting free-text credit entry.
- The schema keeps `Registrations` as one flat table (matching the original
  spec) rather than fully normalizing Student/Faculty/Subject into separate
  linked tables everywhere — `Students`, `Faculty`, and `Subjects` exist as
  lookup/master tables for credit tracking, but `Registrations` still stores
  the denormalized Name/FacultyName columns as originally requested.
