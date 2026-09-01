"""
face_engine.py
--------------
Handles all face_recognition operations:
  - Capturing face images from webcam
  - Generating face encodings from saved images
  - Real-time face recognition loop
"""

import os
import cv2
import numpy as np
import face_recognition
from app.config import (
    DATASET_DIR, WEBCAM_INDEX, CAPTURE_IMAGES,
    RECOGNITION_TOLERANCE, ensure_directories
)
from app import database as db


def get_student_image_dir(student_id: str) -> str:
    """Return the dataset sub-folder for a specific student."""
    path = os.path.join(DATASET_DIR, str(student_id))
    os.makedirs(path, exist_ok=True)
    return path


def capture_student_images(student_id: str, student_name: str,
                            progress_callback=None, status_callback=None) -> bool:
    """
    Open webcam and capture CAPTURE_IMAGES face images for the student.
    
    Args:
        student_id: Unique student ID string
        student_name: Student's display name
        progress_callback: Optional callable(int, int) → (current, total) for progress updates
        status_callback: Optional callable(str) for status messages
    
    Returns:
        True on success, False on failure (webcam unavailable, no faces detected etc.)
    """
    ensure_directories()
    cap = cv2.VideoCapture(WEBCAM_INDEX)

    if not cap.isOpened():
        if status_callback:
            status_callback("❌ Webcam not available. Please check your camera.")
        return False

    save_dir = get_student_image_dir(student_id)
    count = 0
    total = CAPTURE_IMAGES

    if status_callback:
        status_callback(f"📷 Please look at the camera. Capturing {total} images...")

    while count < total:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect faces in current frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb)

        for (top, right, bottom, left) in face_locations:
            # Draw rectangle around face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 212, 170), 2)

        # Overlay text
        cv2.putText(frame, f"Capturing: {count}/{total}  Student: {student_name}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (233, 69, 96), 2)
        cv2.putText(frame, "Press 'q' to cancel",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow("Registering Student - Face Capture", frame)

        # Save frame only when a face is detected
        if face_locations:
            img_path = os.path.join(save_dir, f"{student_id}_{count}.jpg")
            cv2.imwrite(img_path, frame)
            count += 1
            if progress_callback:
                progress_callback(count, total)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return count > 0


def generate_encodings_for_student(student_id: str, student_name: str,
                                   status_callback=None) -> bool:
    """
    Read all saved images for a student, compute face encodings, and store them.
    
    Returns:
        True if at least one encoding was generated, False otherwise.
    """
    image_dir = get_student_image_dir(student_id)
    images = [f for f in os.listdir(image_dir)
              if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

    if not images:
        if status_callback:
            status_callback("❌ No images found. Registration failed.")
        return False

    encodings = []
    for img_file in images:
        img_path = os.path.join(image_dir, img_file)
        try:
            image = face_recognition.load_image_file(img_path)
            enc = face_recognition.face_encodings(image)
            if enc:
                encodings.extend(enc)
        except Exception as e:
            print(f"[FaceEngine] Skipping corrupted image {img_file}: {e}")

    if not encodings:
        if status_callback:
            status_callback("❌ No faces found in captured images. Try again in better lighting.")
        return False

    # Save encodings to database
    db.register_student_encoding(student_id, student_name, encodings)

    if status_callback:
        status_callback(f"✅ {student_name} registered successfully with {len(encodings)} face samples.")
    return True


def run_attendance_recognition(on_recognized=None, on_unknown=None,
                                on_frame=None, stop_flag=None):
    """
    Real-time face recognition loop. Marks attendance for recognized students.
    
    Args:
        on_recognized: Callable(student_id, student_name, marked: bool) - called when face recognized
        on_unknown: Callable() - called when unknown face detected
        on_frame: Callable(frame: np.ndarray) - called for every frame (for preview)
        stop_flag: A threading.Event; loop ends when stop_flag.is_set() returns True
    """
    # Load all encodings from database
    data = db.load_encodings()
    if not data:
        print("[FaceEngine] No registered students found.")
        return

    # Flatten into parallel lists for fast comparison
    known_encodings = []
    known_ids = []
    known_names = []
    for sid, info in data.items():
        for enc in info["encodings"]:
            known_encodings.append(enc)
            known_ids.append(sid)
            known_names.append(info["name"])

    cap = cv2.VideoCapture(WEBCAM_INDEX)
    if not cap.isOpened():
        print("[FaceEngine] Webcam not available.")
        return

    # Track who has been marked in THIS session (avoid spamming)
    session_marked = set()

    while True:
        if stop_flag and stop_flag.is_set():
            break

        ret, frame = cap.read()
        if not ret:
            break

        # Scale down for faster processing, then scale back up for display
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        # Detect face locations and compute encodings
        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(
                known_encodings, face_encoding, tolerance=RECOGNITION_TOLERANCE
            )
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)

            label = "Unknown"
            color = (233, 69, 96)  # red for unknown

            if len(face_distances) > 0:
                best_idx = np.argmin(face_distances)
                if matches[best_idx]:
                    sid = known_ids[best_idx]
                    name = known_names[best_idx]
                    label = f"{name} ({sid})"
                    color = (0, 212, 170)  # teal for known

                    # Mark attendance (returns True if newly marked)
                    marked = db.mark_attendance(sid, name)
                    if sid not in session_marked and marked:
                        session_marked.add(sid)

                    if on_recognized:
                        on_recognized(sid, name, marked)
                else:
                    if on_unknown:
                        on_unknown()

            # Scale face location back to full frame size
            top, right, bottom, left = [v * 2 for v in face_location]

            # Draw box + label on frame
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, label, (left + 4, bottom - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.putText(frame, "Attendance Mode - Press 'q' to stop",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        if on_frame:
            on_frame(frame)
        else:
            cv2.imshow("Face Recognition Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
