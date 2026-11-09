from dotenv import load_dotenv

load_dotenv()
import os
import sys
import subprocess
import uuid
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_from_directory
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from database import (
    create_table,
    add_student,
    get_students,
    delete_student,
    mark_attendance,
    get_attendance,
    get_total_students,
    get_today_attendance,
    get_attendance_percentage
)


# ---------------- CONFIGURATION ----------------

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key-before-deployment"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

UPLOAD_FOLDER = os.path.join(
    app.root_path,
    "student_images"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- ADMIN LOGIN ----------------

ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD_HASH = generate_password_hash(
    os.environ["ADMIN_PASSWORD"]
)

app.secret_key = os.environ["SECRET_KEY"]

# ---------------- LOGIN REQUIRED ----------------

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("admin_logged_in"):
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper


# ---------------- HOME ----------------

@app.route("/")
def index():

    if session.get("admin_logged_in"):
        return redirect(url_for("dashboard"))

    return render_template("index.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("admin_logged_in"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get(
            "username", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        if (
            username == ADMIN_USERNAME
            and check_password_hash(
                ADMIN_PASSWORD_HASH,
                password
            )
        ):

            session.clear()

            session["admin_logged_in"] = True
            session["admin_username"] = username

            return redirect(url_for("dashboard"))

        flash(
            "Invalid username or password.",
            "error"
        )

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout", methods=["POST"])
@login_required
def logout():

    session.clear()

    return redirect(url_for("login"))


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
@login_required
def dashboard():

    total_students = get_total_students()

    present_today = min(
        get_today_attendance(),
        total_students
    )

    absent_today = total_students - present_today

    attendance_percentage = get_attendance_percentage()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        present_today=present_today,
        absent_today=absent_today,
        attendance_percentage=attendance_percentage
    )


# ---------------- REGISTER STUDENT ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get(
            "name", ""
        ).strip()

        roll_no = request.form.get(
            "roll_no", ""
        ).strip()

        department = request.form.get(
            "department", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip()

        photo = request.files.get("photo")

        photo_filename = None

        if not all([
            name,
            roll_no,
            department,
            email
        ]):

            flash(
                "Please fill in all required fields.",
                "error"
            )

            return redirect(url_for("register"))

        if photo and photo.filename:

            original_name = secure_filename(
                photo.filename
            )

            extension = os.path.splitext(
                original_name
            )[1].lower()

            if extension not in [
                ".jpg",
                ".jpeg",
                ".png"
            ]:

                flash(
                    "Please upload a JPG or PNG image.",
                    "error"
                )

                return redirect(url_for("register"))

            photo_filename = str(uuid.uuid4()) + extension

            photo.save(
                os.path.join(
                    UPLOAD_FOLDER,
                    photo_filename
                )
            )

        success = add_student(
            name,
            roll_no,
            department,
            email,
            photo_filename
        )

        if success:

            flash(
                "Student registered successfully!",
                "success"
            )

            return redirect(url_for("students"))

        if photo_filename:

            image_path = os.path.join(
                UPLOAD_FOLDER,
                photo_filename
            )

            if os.path.exists(image_path):
                os.remove(image_path)

        flash(
            "Roll number already exists or registration failed.",
            "error"
        )

    return render_template("register.html")


# ---------------- VIEW STUDENTS ----------------

@app.route("/students")
@login_required
def students():

    students_list = get_students()

    return render_template(
        "students.html",
        students=students_list
    )


# ---------------- STUDENT IMAGE ----------------

@app.route("/student_images/<filename>")
@login_required
def student_image(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ---------------- DELETE STUDENT ----------------

@app.route(
    "/delete_student/<int:student_id>",
    methods=["POST"]
)
@login_required
def delete_student_route(student_id):

    delete_student(student_id)

    flash(
        "Student deleted successfully.",
        "success"
    )

    return redirect(url_for("students"))


# ---------------- VIEW ATTENDANCE ----------------

@app.route("/attendance")
@login_required
def attendance():

    records = get_attendance()

    students_list = get_students()

    return render_template(
        "attendance.html",
        records=records,
        students=students_list
    )


# ---------------- MANUAL ATTENDANCE ----------------

@app.route(
    "/mark_attendance/<int:student_id>",
    methods=["POST"]
)
@login_required
def mark_attendance_route(student_id):

    success = mark_attendance(student_id)

    if success:

        flash(
            "Attendance marked successfully.",
            "success"
        )

    else:

        flash(
            "Attendance already marked today.",
            "error"
        )

    return redirect(url_for("attendance"))


# ---------------- START FACE RECOGNITION ----------------

@app.route(
    "/start_attendance",
    methods=["POST"]
)
@login_required
def start_attendance():

    try:

        subprocess.Popen(
            [sys.executable, "recognize_face.py"],
            cwd=app.root_path
        )

        flash(
            "Face recognition started successfully.",
            "success"
        )

    except Exception:

        flash(
            "Unable to start face recognition.",
            "error"
        )

    return redirect(url_for("attendance"))


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    create_table()

    app.run(debug=True)
