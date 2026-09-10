🎓 Course Registration DBMS

A lightweight desktop registration system where every "Add" and "Withdraw" keeps your credits perfectly in sync — no manual recalculating, no drift, no headaches.

<p align="left"> <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white" alt="Python 3.9+"> <img src="https://img.shields.io/badge/GUI-Tkinter-orange" alt="Tkinter"> <img src="https://img.shields.io/badge/Database-MS%20Access-A4373A?logo=microsoftaccess&logoColor=white" alt="MS Access"> <img src="https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white" alt="Windows"> <img src="https://img.shields.io/badge/status-mini--project-brightgreen" alt="Status"> </p>

Built as a DBMS mini-project, this app pairs a clean Python + Tkinter interface with a Microsoft Access backend (via pyodbc) to handle the full lifecycle of a student's course load — with every credit accounted for, transaction by transaction.

✨ What it does
	
🧑‍🎓 Student Portal	Add / withdraw your own courses, see your live credit total

🧑‍🏫 Faculty Portal	Reassign slots & faculty, view every student's registrations

➕ Add Course	One of the 3 core operations from the spec

➖ Withdraw Course	Cleanly removes a registration and rebalances credits

🔄 Update Registration	Faculty can change slot / faculty assignments

🔒 Always-Accurate Credits	Every Add/Withdraw runs inside one transaction — TotalCredits can never drift out of sync

🛠️ Tech Stack
Frontend: Python 3.9+ with Tkinter
Backend: Microsoft Access (.accdb)
Bridge: pyodbc

📋 Requirements
Windows with Microsoft Access, or just the free Access Database Engine redistributable
Python 3.9+
pip install pyodbc

⚠️ Bitness must match — 64-bit Python needs the 64-bit Access driver (and vice versa).


🚀 Getting Started

**1️⃣ Create the database**
Open Microsoft Access → File → New → Blank Database
Name it exactly CourseDB.accdb
Save it in the same folder as app.py / setup_db.py
Close it in Access — don't leave it open while running scripts

**2️⃣ Build the tables**
bash
python setup_db.py

This spins up 4 tables: Students, Faculty, Subjects, Registrations.


**3️⃣ Launch the app**
bash
python app.py

🧑‍🎓 Student → enter Reg. No + Name → add/withdraw courses

🧑‍🏫 Faculty → enter Faculty ID + Name → update registrations, view all records

📁 Project Structure
File	Purpose
setup_db.py	One-time script that creates the Access tables
db.py	All SQL / pyodbc logic — Add, Withdraw, Update, lookups
app.py	Tkinter GUI — login screen + role-based tabs
💡 Notes & Possible Extensions
Subjects.Credits is currently entered by the student on first Add. A stricter version could have faculty/admin pre-populate the subject catalog instead of trusting free-text entry.
Registrations is kept as one flat table (per the original spec) rather than fully normalized — Students, Faculty, and Subjects serve as lookup/master tables for credit tracking, while Registrations still stores denormalized Name/FacultyName columns as originally requested.
<p align="center"><i>Built with ☕, Tkinter, and a healthy respect for transaction integrity.</i></p>
