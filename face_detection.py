
import cv2

# Load OpenCV's pre-trained face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Check whether the face detector loaded
if face_cascade.empty():
    print("Error: Face detector could not be loaded!")
    exit()

# Open webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Webcam not detected!")
    exit()

print("Face Detection Started!")
print("Press Q to close.")

while True:

    success, frame = camera.read()

    if not success:
        print("Unable to capture video.")
        break

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30, 30)
    )

    # Draw rectangles around detected faces
    for (x, y, w, h) in faces:

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Face Detected",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    # Display number of detected faces
    cv2.putText(
        frame,
        f"Faces: {len(faces)}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 0, 0),
        2
    )

    cv2.imshow("Smart Attendance - Face Detection", frame)

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
