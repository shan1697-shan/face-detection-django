import cv2
import os
import face_recognition
import numpy as np
import pickle
import pandas as pd
from datetime import datetime

# Paths for saving data
ENCODINGS_PATH = "face_encodings.pkl"
DATA_DIR = "face_data"
ATTENDANCE_FILE = "attendance.xlsx"

def check_camera_access():
    """Test if the camera can be accessed."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to access camera on index 0. Trying index 1.")
        cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Unable to access camera on index 1 as well. Please check your camera connection.")
        return None
    print("Camera successfully accessed.")
    return cap

def collect_data(name):
    """Collect face images for a given name."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    cap = check_camera_access()
    if cap is None:
        return

    count = 0
    print(f"Collecting data for {name}. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break

        # Detect face in frame
        face_locations = face_recognition.face_locations(frame)
        for (top, right, bottom, left) in face_locations:
            face_image = frame[top:bottom, left:right]
            face_path = os.path.join(DATA_DIR, f"{name}_{count}.jpg")
            cv2.imwrite(face_path, face_image)
            count += 1

        cv2.imshow("Collecting Data", frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or count >= 20:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Collected {count} images for {name}.")

def train_model():
    """Encode faces from collected images and save encodings."""
    encodings = []
    names = []

    for image_name in os.listdir(DATA_DIR):
        image_path = os.path.join(DATA_DIR, image_name)
        name = image_name.split("_")[0]
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)

        if face_encodings:
            encodings.append(face_encodings[0])
            names.append(name)

    with open(ENCODINGS_PATH, "wb") as file:
        pickle.dump((encodings, names), file)
    print("Training complete and encodings saved.")



def mark_attendance(name):
    """Marks attendance in the Excel file."""
    now = datetime.now()
    today_date = now.strftime("%Y-%m-%d")
    time_now = now.strftime("%H:%M:%S")

    # Check if the attendance file exists; if not, create it
    if not os.path.exists(ATTENDANCE_FILE):
        df = pd.DataFrame(columns=["Date", "Name", "Time"])
        df.to_excel(ATTENDANCE_FILE, index=False)

    # Load the attendance file
    df = pd.read_excel(ATTENDANCE_FILE)

    # Check if the person is already marked for today
    if not ((df["Date"] == today_date) & (df["Name"] == name)).any():
        # Append the new entry
        new_entry = pd.DataFrame({"Date": [today_date], "Name": [name], "Time": [time_now]})
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_excel(ATTENDANCE_FILE, index=False)
        print(f"Marked attendance for {name} at {time_now}.")
    else:
        print(f"{name}'s attendance is already marked for today.")

def recognize_faces():
    """Recognize faces in real-time using trained encodings."""
    with open(ENCODINGS_PATH, "rb") as file:
        known_encodings, known_names = pickle.load(file)

    cap = check_camera_access()
    if cap is None:
        return

    print("Starting face recognition. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break

        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            name = "Unknown"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]

                mark_attendance(name)
                
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Main interactive menu
print("Welcome to the Face Recognition Attendance System")
choice = input("Enter '1' to collect data, '2' to train model, or '3' to recognize faces in real-time: ")

if choice == '1':
    name = input("Enter the name of the person: ")
    collect_data(name)
elif choice == '2':
    train_model()
elif choice == '3':
    recognize_faces()
else:
    print("Invalid choice.")
