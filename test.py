import cv2

def test_camera():
    cap = cv2.VideoCapture(0)  # Replace 0 with 1 or 2 if needed
    if not cap.isOpened():
        print("Cannot open camera")
        return
    print("Camera opened successfully. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break
        cv2.imshow("Camera Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

test_camera()
