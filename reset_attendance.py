
import sqlite3

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

confirm = input(
    "Are you sure you want to delete ALL attendance records? (yes/no): "
)

if confirm.lower() == "yes":
    cursor.execute("DELETE FROM attendance")
    cursor.execute(
        "DELETE FROM sqlite_sequence WHERE name = 'attendance'"
    )
    conn.commit()
    print("All attendance records have been reset successfully!")
else:
    print("Reset cancelled.")

conn.close()
