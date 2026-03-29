import sqlite3

DATABASE = "placement.db"

def get_db():
    conn = sqlite3.connect(DATABASE, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_db()
    cur = conn.cursor()

    # ADMIN
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    # STUDENTS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        phone TEXT,
        branch TEXT,
        cgpa TEXT,
        resume TEXT,
        status TEXT DEFAULT 'active'
    )
    """)

    # COMPANIES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS companies(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        hr_contact TEXT,
        website TEXT,
        approval_status TEXT DEFAULT 'pending',
        status TEXT DEFAULT 'active'
    )
    """)

    # DRIVES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS drives(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        job_title TEXT,
        description TEXT,
        eligibility TEXT,
        deadline TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    # APPLICATIONS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS applications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        drive_id INTEGER,
        application_date TEXT,
        status TEXT DEFAULT 'Applied',
        UNIQUE(student_id,drive_id)
    )
    """)

    conn.commit()

    cur.execute("SELECT * FROM admin")

    if not cur.fetchone():
        cur.execute("INSERT INTO admin(username,password) VALUES('admin','admin123')")
        conn.commit()

    conn.close()