
import cv2

# Open the default webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Error: Webcam not detected!")
    exit()

print("Webcam connected successfully!")
print("Press Q to close the camera.")

while True:
    success, frame = camera.read()

    if not success:
        print("Unable to capture video.")
        break

    cv2.imshow("Smart Attendance - Camera Test", frame)

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
