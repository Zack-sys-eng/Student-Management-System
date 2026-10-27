from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = "student_management_secret_key"

# Use an absolute path so SQLite always opens the correct database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "students.db")

def get_db():
    connection = sqlite3.connect(
        DATABASE,
        timeout=15,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA busy_timeout = 15000")

    connection.execute("PRAGMA journal_mode = WAL")

    return connection

def init_db():

    db = get_db()

    try:

        db.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                gender TEXT,
                age INTEGER,
                course TEXT,
                semester TEXT,
                department TEXT,
                address TEXT,
                marks REAL DEFAULT 0,
                attendance REAL DEFAULT 0
            )
        """)

        db.commit()

    finally:

        db.close()

def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "logged_in" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return decorated_function

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":

            session["logged_in"] = True
            session["username"] = username

            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():

    db = get_db()

    try:

        total_students = db.execute(
            "SELECT COUNT(*) FROM students"
        ).fetchone()[0]

        average_marks = db.execute(
            "SELECT AVG(marks) FROM students"
        ).fetchone()[0]

        average_attendance = db.execute(
            "SELECT AVG(attendance) FROM students"
        ).fetchone()[0]

        passed_students = db.execute(
            "SELECT COUNT(*) FROM students WHERE marks >= 40"
        ).fetchone()[0]

        recent_students = db.execute(
            "SELECT * FROM students ORDER BY id DESC LIMIT 5"
        ).fetchall()

    finally:

        db.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        average_marks=round(average_marks or 0, 2),
        average_attendance=round(average_attendance or 0, 2),
        passed_students=passed_students,
        recent_students=recent_students
    )

@app.route("/students")
@login_required
def students():

    search = request.args.get("search", "")

    db = get_db()

    try:

        if search:

            student_list = db.execute("""
                SELECT * FROM students
                WHERE student_id LIKE ?
                OR name LIKE ?
                OR course LIKE ?
                OR department LIKE ?
                ORDER BY id DESC
            """, (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
                f"%{search}%"
            )).fetchall()

        else:

            student_list = db.execute(
                "SELECT * FROM students ORDER BY id DESC"
            ).fetchall()

    finally:

        db.close()

    return render_template(
        "students.html",
        students=student_list,
        search=search
    )

@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():

    if request.method == "POST":

        student_id = request.form.get("student_id")
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        gender = request.form.get("gender")
        age = request.form.get("age")
        course = request.form.get("course")
        semester = request.form.get("semester")
        department = request.form.get("department")
        address = request.form.get("address")
        marks = request.form.get("marks") or 0
        attendance = request.form.get("attendance") or 0

        db = get_db()

        try:

            db.execute("""
                INSERT INTO students
                (
                    student_id,
                    name,
                    email,
                    phone,
                    gender,
                    age,
                    course,
                    semester,
                    department,
                    address,
                    marks,
                    attendance
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id,
                name,
                email,
                phone,
                gender,
                age,
                course,
                semester,
                department,
                address,
                marks,
                attendance
            ))

            db.commit()

            flash("Student added successfully!", "success")

            return redirect(url_for("students"))

        except sqlite3.IntegrityError:

            db.rollback()

            flash(
                "Student ID already exists! Please use a different ID.",
                "danger"
            )

        except sqlite3.Error as error:

            db.rollback()

            flash(
                f"Database error: {error}",
                "danger"
            )

        finally:

            db.close()

    return render_template("add_student.html")

@app.route("/students/<int:student_id>")
@login_required
def student_details(student_id):

    db = get_db()

    try:

        student = db.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

    finally:

        db.close()

    if student is None:

        flash("Student not found.", "danger")

        return redirect(url_for("students"))

    return render_template(
        "student_details.html",
        student=student
    )

@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):

    db = get_db()

    try:

        student = db.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        ).fetchone()

    finally:

        db.close()

    if student is None:

        flash("Student not found.", "danger")

        return redirect(url_for("students"))

    if request.method == "POST":

        updated_student_id = request.form.get("student_id")
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        gender = request.form.get("gender")
        age = request.form.get("age")
        course = request.form.get("course")
        semester = request.form.get("semester")
        department = request.form.get("department")
        address = request.form.get("address")
        marks = request.form.get("marks") or 0
        attendance = request.form.get("attendance") or 0

        db = get_db()

        try:

            db.execute("""
                UPDATE students
                SET
                    student_id = ?,
                    name = ?,
                    email = ?,
                    phone = ?,
                    gender = ?,
                    age = ?,
                    course = ?,
                    semester = ?,
                    department = ?,
                    address = ?,
                    marks = ?,
                    attendance = ?
                WHERE id = ?
            """, (
                updated_student_id,
                name,
                email,
                phone,
                gender,
                age,
                course,
                semester,
                department,
                address,
                marks,
                attendance,
                student_id
            ))

            db.commit()

            flash(
                "Student updated successfully!",
                "success"
            )

            return redirect(url_for("students"))

        except sqlite3.IntegrityError:

            db.rollback()

            flash(
                "Student ID already exists! Please use a different ID.",
                "danger"
            )

        except sqlite3.Error as error:

            db.rollback()

            flash(
                f"Database error: {error}",
                "danger"
            )

        finally:

            db.close()

    return render_template(
        "edit_student.html",
        student=student
    )

@app.route("/students/delete/<int:student_id>", methods=["POST"])
@login_required
def delete_student(student_id):

    db = get_db()

    try:

        db.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

        db.commit()

        flash(
            "Student deleted successfully!",
            "success"
        )

    except sqlite3.Error as error:

        db.rollback()

        flash(
            f"Database error: {error}",
            "danger"
        )

    finally:

        db.close()

    return redirect(url_for("students"))

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )