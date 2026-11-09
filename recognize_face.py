import cv2
import numpy as np
from database import mark_attendance

# Load trained face recognition model
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("face_model.yml")

# Load student information
student_info = np.load(
    "student_labels.npy",
    allow_pickle=True
).item()

# Load face detector
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# Start webcam
camera = cv2.VideoCapture(0)

# Keep track of students already processed
marked_students = set()

while True:
    ret, frame = camera.read()

    if not ret:
        print("Unable to access camera")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    detected_faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50)
    )

    for (x, y, w, h) in detected_faces:

        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))

        label, confidence = recognizer.predict(face)
        print(
            "Predicted ID:", label,
            "| Confidence:", round(confidence, 2),
            "| Student:", student_info.get(label, "Not found")
        )

        if confidence < 60 and label in student_info:

            student = student_info[label]
            student_id = int(label)
            name = student["name"]
            roll_no = student["roll_no"]

            if student_id not in marked_students:

                success = mark_attendance(student_id)

                if success:
                    print(name, "- Attendance marked Present!")
                else:
                    print(name, "- Attendance already marked today!")

                marked_students.add(student_id)

            text = name + " - Present"
            color = (0, 255, 0)

        else:
            text = "Unknown"
            color = (0, 0, 255)

        cv2.rectangle(
            frame,
            (x, y),
            (x+w, y+h),
            color,
            2
        )

        cv2.putText(
            frame,
            text,
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2
        )

    cv2.imshow("Smart Attendance System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()