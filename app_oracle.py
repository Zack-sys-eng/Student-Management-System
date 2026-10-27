from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import oracledb

app = Flask(__name__)
app.secret_key = "student_management_secret_key"

ORACLE_USER = "STUDENT_APP"
ORACLE_PASSWORD = "StudentApp_2026"
ORACLE_DSN = "localhost:1521/XEPDB1"

def get_db():
    return oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def rows_to_dicts(cursor, rows):
    columns = [column[0].lower() for column in cursor.description]
    return [dict(zip(columns, row)) for row in rows]


def row_to_dict(cursor, row):
    if row is None:
        return None

    columns = [column[0].lower() for column in cursor.description]
    return dict(zip(columns, row))

def get_student(student_id):
    connection = get_db()

    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM students WHERE id = :student_id",
            {"student_id": student_id}
        )

        student = row_to_dict(cursor, cursor.fetchone())
        cursor.close()

        return student

    finally:
        connection.close()

def get_form_values(form):
    age = form.get("age", "").strip()
    semester = form.get("semester", "").strip()
    marks = form.get("marks", "").strip()
    attendance = form.get("attendance", "").strip()

    return {
        "student_id": form.get("student_id", "").strip(),
        "name": form.get("name", "").strip(),
        "email": form.get("email", "").strip(),
        "phone": form.get("phone", "").strip(),
        "gender": form.get("gender", "").strip(),
        "age": int(age) if age else None,
        "course": form.get("course", "").strip(),
        "semester": int(semester) if semester else None,
        "department": form.get("department", "").strip(),
        "address": form.get("address", "").strip(),
        "marks": float(marks) if marks else 0,
        "attendance": float(attendance) if attendance else 0
    }

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == "admin" and password == "admin123":
            session["logged_in"] = True
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    connection = get_db()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                COUNT(*) AS total_students,
                NVL(AVG(marks), 0) AS average_marks,
                NVL(AVG(attendance), 0) AS average_attendance,
                SUM(CASE WHEN marks >= 40 THEN 1 ELSE 0 END) AS passed_students
            FROM students
        """)

        stats = row_to_dict(cursor, cursor.fetchone())

        cursor.execute("""
            SELECT *
            FROM (
                SELECT *
                FROM students
                ORDER BY id DESC
            )
            WHERE ROWNUM <= 5
        """)

        recent_students = rows_to_dicts(cursor, cursor.fetchall())

        cursor.close()

        return render_template(
            "dashboard.html",
            stats=stats,
            recent_students=recent_students
        )

    finally:
        connection.close()

@app.route("/students")
@login_required
def students():
    search = request.args.get("search", "").strip()
    connection = get_db()

    try:
        cursor = connection.cursor()

        if search:
            search_value = f"%{search}%"

            cursor.execute("""
                SELECT *
                FROM students
                WHERE LOWER(name) LIKE LOWER(:p1)
                   OR LOWER(student_id) LIKE LOWER(:p2)
                   OR LOWER(email) LIKE LOWER(:p3)
                ORDER BY id DESC
            """, {
                "p1": search_value,
                "p2": search_value,
                "p3": search_value
            })
        else:
            cursor.execute("SELECT * FROM students ORDER BY id DESC")

        student_list = rows_to_dicts(cursor, cursor.fetchall())
        cursor.close()

        return render_template(
            "students.html",
            students=student_list,
            search=search
        )

    finally:
        connection.close()

@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():

    if request.method == "POST":

        print("\n" + "=" * 50)
        print("ADD STUDENT FORM SUBMITTED")
        print("FORM DATA:", dict(request.form))
        print("=" * 50)

        connection = None
        cursor = None

        try:
            data = get_form_values(request.form)

            # Validate required fields
            if not data["student_id"] or not data["name"]:
                flash("Student ID and Name are required.", "error")
                print("SAVE STOPPED: Student ID or Name is missing.")
                return redirect(url_for("add_student"))

            connection = get_db()
            cursor = connection.cursor()

            print("Connected to Oracle successfully.")
            print("Attempting to insert student:", data["student_id"])

            cursor.execute("""
                INSERT INTO students (
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
                VALUES (
                    :student_id,
                    :name,
                    :email,
                    :phone,
                    :gender,
                    :age,
                    :course,
                    :semester,
                    :department,
                    :address,
                    :marks,
                    :attendance
                )
            """, data)

            connection.commit()

            print("STUDENT SAVED SUCCESSFULLY")
            print("Oracle transaction committed.")

            flash("Student added successfully!", "success")
            return redirect(url_for("students"))

        except oracledb.IntegrityError as error:
            if connection:
                connection.rollback()

            print("ORACLE INTEGRITY ERROR:", error)

            flash(
                "Cannot save student. Check whether the Student ID already exists.",
                "error"
            )

        except oracledb.DatabaseError as error:
            if connection:
                connection.rollback()

            print("ORACLE DATABASE ERROR WHILE SAVING:", error)

            flash(
                "Oracle could not save the student. Check the VS Code terminal.",
                "error"
            )

        except (ValueError, TypeError) as error:
            if connection:
                connection.rollback()

            print("INVALID FORM DATA:", error)

            flash(
                "Please check the Age, Semester, Marks and Attendance fields.",
                "error"
            )

        except Exception as error:
            if connection:
                connection.rollback()

            print("UNEXPECTED ERROR WHILE SAVING:", repr(error))

            flash("An unexpected error occurred. Check the terminal.", "error")

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()

        return redirect(url_for("add_student"))

    return render_template("add_student.html")


@app.route("/students/<int:student_id>")
@login_required
def student_details(student_id):
    student = get_student(student_id)

    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("students"))

    return render_template("student_details.html", student=student)

@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    student = get_student(student_id)

    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("students"))

    if request.method == "POST":
        connection = None
        cursor = None

        try:
            data = get_form_values(request.form)

            if not data["student_id"] or not data["name"]:
                flash("Student ID and Name are required.", "error")
                return redirect(
                    url_for("edit_student", student_id=student_id)
                )

            connection = get_db()
            cursor = connection.cursor()

            data["id"] = student_id

            cursor.execute("""
                UPDATE students
                SET student_id = :student_id,
                    name = :name,
                    email = :email,
                    phone = :phone,
                    gender = :gender,
                    age = :age,
                    course = :course,
                    semester = :semester,
                    department = :department,
                    address = :address,
                    marks = :marks,
                    attendance = :attendance
                WHERE id = :id
            """, data)

            connection.commit()

            print("STUDENT UPDATED SUCCESSFULLY:", student_id)

            flash("Student updated successfully!", "success")
            return redirect(
                url_for("student_details", student_id=student_id)
            )

        except Exception as error:
            if connection:
                connection.rollback()

            print("ERROR UPDATING STUDENT:", repr(error))
            flash("Could not update student. Check the terminal.", "error")

        finally:
            if cursor:
                cursor.close()

            if connection:
                connection.close()

        return redirect(url_for("edit_student", student_id=student_id))

    return render_template("edit_student.html", student=student)

@app.route("/students/delete/<int:student_id>", methods=["POST"])
@login_required
def delete_student(student_id):
    connection = None
    cursor = None

    try:
        connection = get_db()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM students WHERE id = :student_id",
            {"student_id": student_id}
        )

        connection.commit()

        print("STUDENT DELETED:", student_id)
        flash("Student deleted successfully!", "success")

    except Exception as error:
        if connection:
            connection.rollback()

        print("ERROR DELETING STUDENT:", repr(error))
        flash("Could not delete student. Check the terminal.", "error")

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()

    return redirect(url_for("students"))

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )