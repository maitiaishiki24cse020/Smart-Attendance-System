import cv2
import numpy as np
import os

from database import connect_db

FACES_FOLDER = "student_faces"

faces = []
labels = []
student_info = {}

# Get registered students
conn = connect_db()
cursor = conn.cursor()

cursor.execute("SELECT id, name, roll_no FROM students")
students = cursor.fetchall()

conn.close()

for student_id, name, roll_no in students:

    folder = os.path.join(FACES_FOLDER, str(student_id))

    if not os.path.exists(folder):
        print("No face folder found for:", name)
        continue

    student_info[student_id] = {
        "name": name,
        "roll_no": roll_no
    }

    for filename in os.listdir(folder):

        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        image_path = os.path.join(folder, filename)
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if image is None:
            continue

        face = cv2.resize(image, (200, 200))

        faces.append(face)
        labels.append(student_id)

        print("Training:", name, "-", filename)

if len(faces) == 0:
    print("No training images found!")
    exit()

# Train LBPH recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

recognizer.train(
    faces,
    np.array(labels, dtype=np.int32)
)

recognizer.write("face_model.yml")

np.save("student_labels.npy", student_info)

print("\nFace recognition training completed!")
print("Total training images:", len(faces))
print("Total students:", len(student_info))
print("Model saved successfully!")