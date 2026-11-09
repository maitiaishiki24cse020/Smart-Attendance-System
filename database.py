
import sqlite3
from datetime import datetime


def connect_db():
    return sqlite3.connect("attendance.db")


def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            email TEXT NOT NULL,
            photo TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date DATE NOT NULL,
            attendance_time TIME NOT NULL,
            status TEXT DEFAULT 'Present',
            UNIQUE(student_id, attendance_date),
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()


def add_student(name, roll_no, department, email, photo):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO students
            (name, roll_no, department, email, photo)
            VALUES (?, ?, ?, ?, ?)
        """, (name, roll_no, department, email, photo))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def get_students():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    students = cursor.fetchall()

    conn.close()
    return students


def delete_student(student_id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "DELETE FROM attendance WHERE student_id = ?",
            (student_id,)
        )

        cursor.execute(
            "DELETE FROM students WHERE id = ?",
            (student_id,)
        )

        conn.commit()

    finally:
        conn.close()


def mark_attendance(student_id):
    conn = connect_db()
    cursor = conn.cursor()
    now = datetime.now()

    try:
        cursor.execute("""
            INSERT INTO attendance
            (student_id, attendance_date, attendance_time, status)
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S"),
            "Present"
        ))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def get_attendance():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            students.name,
            students.roll_no,
            attendance.attendance_date,
            attendance.attendance_time,
            attendance.status
        FROM attendance
        JOIN students
        ON students.id = attendance.student_id
        ORDER BY attendance.id DESC
    """)

    records = cursor.fetchall()
    conn.close()

    return records


# NEW: Total registered students
def get_total_students():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]

    conn.close()
    return total


# NEW: Students present today
def get_today_attendance():
    conn = connect_db()
    cursor = conn.cursor()

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE attendance_date = ?
        AND status = 'Present'
    """, (today,))

    total = cursor.fetchone()[0]

    conn.close()
    return total


# NEW: Attendance percentage today
def get_attendance_percentage():
    total_students = get_total_students()

    if total_students == 0:
        return 0

    present_students = get_today_attendance()

    percentage = (min(present_students, total_students)
                  / total_students) * 100

    return round(percentage, 2)


if __name__ == "__main__":
    create_table()
    print("Total Students:", get_total_students())
    print("Present Today:", get_today_attendance())
    print("Attendance Percentage:", get_attendance_percentage(), "%")
