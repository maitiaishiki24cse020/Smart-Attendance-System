import cv2
import os
from database import connect_db

# Load face detector
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# Get registered students
conn = connect_db()
cursor = conn.cursor()

cursor.execute("SELECT id, name, roll_no FROM students")
students = cursor.fetchall()

conn.close()

if not students:
    print("No students registered!")
    exit()

# Display students
print("\nRegistered Students:")

for i, student in enumerate(students):
    print(
        i + 1, ".", student[1],
        "| Roll Number:", student[2]
    )

# Select student
choice = int(input("\nSelect student number: "))

if choice < 1 or choice > len(students):
    print("Invalid selection!")
    exit()

student_id, name, roll_no = students[choice - 1]

# Create student folder
folder = os.path.join("student_faces", str(student_id))
os.makedirs(folder, exist_ok=True)

# Start webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Unable to open webcam!")
    exit()

count = len([
    file for file in os.listdir(folder)
    if file.lower().endswith((".jpg", ".jpeg", ".png"))
])

print("\nCapturing faces for:", name)
print("Press S to save a face image.")
print("Press Q to quit.")

while count < 15:

    ret, frame = camera.read()

    if not ret:
        print("Camera error!")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    detected_faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    largest_face = None

    if len(detected_faces) > 0:
        largest_face = max(
            detected_faces,
            key=lambda box: box[2] * box[3]
        )

        x, y, w, h = largest_face

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

    cv2.putText(
        frame,
        f"Student: {name}",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Photos: {count}/15",
        (20, 65),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    cv2.imshow("Face Data Collection", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('s') or key == ord('S'):

        if largest_face is not None:

            x, y, w, h = largest_face

            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200, 200))

            count += 1

            filename = os.path.join(
                folder,
                f"face_{count}.jpg"
            )

            cv2.imwrite(filename, face)

            print("Saved:", filename)

        else:
            print("No face detected! Try again.")

    elif key == ord('q') or key == ord('Q'):
        break
q
camera.release()
cv2.destroyAllWindows()

print("\nFace collection completed!")
print("Total photos:", count)