from flask import Flask, render_template, request, redirect, session
from models import get_db, create_tables
import datetime

app = Flask(__name__)
app.secret_key = "secret"

# Automatically create tables
create_tables()


# ------------------ HOME PAGE ------------------
@app.route("/")
def index():
    return render_template("index.html")


# ------------------ LOGIN ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db()
        cur = conn.cursor()

        user = None

        if role == "admin":
            cur.execute("SELECT * FROM admin WHERE username=? AND password=?", (email, password))
            user = cur.fetchone()
            if user:
                session["admin"] = True
                return redirect("/admin/dashboard")

        elif role == "student":
            cur.execute("SELECT * FROM students WHERE email=? AND password=?", (email, password))
            user = cur.fetchone()
            if user:
                session["student_id"] = user["id"]
                return redirect("/student/dashboard")

        elif role == "company":
            cur.execute(
                "SELECT * FROM companies WHERE email=? AND password=? AND approval_status='approved'",
                (email, password)
            )
            user = cur.fetchone()
            if user:
                session["company_id"] = user["id"]
                return redirect("/company/dashboard")

        conn.close()

    return render_template("login.html")


# ------------------ STUDENT REGISTER ------------------
@app.route("/register_student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone = request.form.get("phone")

        conn = get_db()
        cur = conn.cursor()

        cur.execute("INSERT INTO students(name,email,password,phone) VALUES(?,?,?,?)",
                    (name, email, password, phone))
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register_student.html")


# ------------------ COMPANY REGISTER ------------------
@app.route("/register_company", methods=["GET", "POST"])
def register_company():
    if request.method == "POST":
        cname = request.form.get("company_name")
        email = request.form.get("email")
        password = request.form.get("password")
        hr = request.form.get("hr_contact")
        website = request.form.get("website")

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO companies(company_name,email,password,hr_contact,website) VALUES(?,?,?,?,?)",
            (cname, email, password, hr, website)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register_company.html")


# ------------------ ADMIN DASHBOARD ------------------
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM companies")
    companies = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM drives")
    drives = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM applications")
    applications = cur.fetchone()[0]

    conn.close()

    return render_template("admin_dashboard.html", students=students, companies=companies,
                           drives=drives, applications=applications)


# ------------------ ADMIN STUDENTS ------------------
@app.route("/admin/students")
def admin_students():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    conn.close()

    return render_template("admin_students.html", students=students)


@app.route("/admin/delete_student/<int:id>")
def delete_student(id):
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin/students")


@app.route("/admin/blacklist_student/<int:id>")
def blacklist_student(id):
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE students SET status='blacklisted' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin/students")


# ------------------ ADMIN COMPANIES ------------------
@app.route("/admin/companies")
def admin_companies():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM companies")
    companies = cur.fetchall()
    conn.close()

    return render_template("admin_companies.html", companies=companies)


@app.route("/admin/approve_company/<int:id>")
def approve_company(id):
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE companies SET approval_status='approved' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin/companies")


@app.route("/admin/reject_company/<int:id>")
def reject_company(id):
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE companies SET approval_status='rejected' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin/companies")


@app.route("/admin/blacklist_company/<int:id>")
def blacklist_company(id):
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE companies SET status='blacklisted' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin/companies")


# ------------------ ADMIN DRIVES ------------------
@app.route("/admin/drives")
def admin_drives():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT drives.*, companies.company_name
        FROM drives
        JOIN companies ON drives.company_id = companies.id
    """)
    drives = cur.fetchall()
    conn.close()

    return render_template("admin_drives.html", drives=drives)


@app.route("/admin/approve_drive/<int:id>")
def approve_drive(id):
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE drives SET status='approved' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin/drives")


@app.route("/admin/reject_drive/<int:id>")
def reject_drive(id):
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE drives SET status='rejected' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/admin/drives")


# ------------------ ADMIN SEARCH ------------------
@app.route("/admin/search_student", methods=["POST"])
def search_student():
    if not session.get("admin"):
        return redirect("/login")

    keyword = request.form.get("keyword")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE name LIKE ? OR id LIKE ?", ('%'+keyword+'%', '%'+keyword+'%'))
    students = cur.fetchall()
    conn.close()

    return render_template("admin_students.html", students=students)


@app.route("/admin/search_company", methods=["POST"])
def search_company():
    if not session.get("admin"):
        return redirect("/login")

    keyword = request.form.get("keyword")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM companies WHERE company_name LIKE ?", ('%'+keyword+'%',))
    companies = cur.fetchall()
    conn.close()

    return render_template("admin_companies.html", companies=companies)


# ------------------ COMPANY DASHBOARD ------------------
@app.route("/company/dashboard")
def company_dashboard():
    if not session.get("company_id"):
        return redirect("/login")

    company_id = session["company_id"]
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM drives WHERE company_id=?", (company_id,))
    drives = cur.fetchall()
    conn.close()

    return render_template("company_dashboard.html", drives=drives)


# ------------------ CREATE DRIVE ------------------
@app.route("/company/create_drive", methods=["GET", "POST"])
def create_drive():
    if not session.get("company_id"):
        return redirect("/login")

    if request.method == "POST":
        company_id = session["company_id"]
        title = request.form.get("title")
        description = request.form.get("description")
        eligibility = request.form.get("eligibility")
        deadline = request.form.get("deadline")

        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO drives(company_id,job_title,description,eligibility,deadline) VALUES(?,?,?,?,?)",
                    (company_id, title, description, eligibility, deadline))
        conn.commit()
        conn.close()

        return redirect("/company/dashboard")

    return render_template("create_drive.html")


# ------------------ STUDENT DASHBOARD ------------------
@app.route("/student/dashboard")
def student_dashboard():
    if not session.get("student_id"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT drives.*, companies.company_name
        FROM drives
        JOIN companies ON drives.company_id = companies.id
        WHERE drives.status='approved'
    """)
    drives = cur.fetchall()
    conn.close()

    return render_template("student_dashboard.html", drives=drives)


# ------------------ APPLY DRIVE ------------------
@app.route("/apply/<int:drive_id>")
def apply_drive(drive_id):
    if not session.get("student_id"):
        return redirect("/login")

    student_id = session["student_id"]
    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO applications(student_id,drive_id,application_date) VALUES(?,?,?)",
                    (student_id, drive_id, str(datetime.date.today())))
        conn.commit()
    except:
        pass

    conn.close()
    return redirect("/student/dashboard")


# ------------------ COMPANY VIEW APPLICATIONS ------------------
@app.route("/company/applications/<int:drive_id>")
def company_applications(drive_id):
    if not session.get("company_id"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT applications.id, students.name, students.email, students.phone, applications.status
        FROM applications
        JOIN students ON applications.student_id = students.id
        WHERE applications.drive_id=?
    """, (drive_id,))
    apps = cur.fetchall()
    conn.close()

    return render_template("company_applications.html", apps=apps)


@app.route("/company/shortlist/<int:app_id>")
def shortlist_student(app_id):
    if not session.get("company_id"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE applications SET status='Shortlisted' WHERE id=?", (app_id,))
    conn.commit()
    conn.close()

    return redirect(request.referrer)


@app.route("/company/reject_student/<int:app_id>")
def reject_student(app_id):
    if not session.get("company_id"):
        return redirect("/login")

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE applications SET status='Rejected' WHERE id=?", (app_id,))
    conn.commit()
    conn.close()

    return redirect(request.referrer)


# ------------------ STUDENT PROFILE ------------------
@app.route("/student/profile", methods=["GET", "POST"])
def student_profile():
    if not session.get("student_id"):
        return redirect("/login")

    student_id = session["student_id"]
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        branch = request.form.get("branch")
        cgpa = request.form.get("cgpa")

        cur.execute("UPDATE students SET name=?, phone=?, branch=?, cgpa=? WHERE id=?",
                    (name, phone, branch, cgpa, student_id))
        conn.commit()

    cur.execute("SELECT * FROM students WHERE id=?", (student_id,))
    student = cur.fetchone()
    conn.close()

    return render_template("student_profile.html", student=student)


# ------------------ STUDENT APPLICATIONS ------------------
@app.route("/student/applications")
def student_applications():
    if not session.get("student_id"):
        return redirect("/login")

    student_id = session["student_id"]
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT drives.job_title, companies.company_name, applications.status, applications.application_date
        FROM applications
        JOIN drives ON applications.drive_id = drives.id
        JOIN companies ON drives.company_id = companies.id
        WHERE applications.student_id=?
    """, (student_id,))
    apps = cur.fetchall()
    conn.close()

    return render_template("student_applications.html", apps=apps)


# ------------------ LOGOUT ------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)