# Face Recognition Attendance System

A Python-based **Face Recognition Attendance System** that uses a webcam to recognize registered students and automatically record their attendance with the date and time.

## 📌 Project Overview

The Face Recognition Attendance System is designed to automate the traditional attendance process. Instead of manually calling names or signing an attendance sheet, the system identifies students using facial recognition technology.

The system captures a student's face during registration, generates face encodings, and later compares faces detected through the webcam with the registered faces.

When a registered student is recognized, their attendance is automatically recorded.

## 🎯 Objectives

* Automate the student attendance process.
* Reduce manual attendance work.
* Use face recognition for student identification.
* Record attendance with date and time.
* Prevent duplicate attendance on the same day.
* Provide an easy-to-use graphical interface.
* Maintain attendance records digitally.

## ✨ Features

* 👤 Student registration
* 📷 Webcam-based face capture
* 🧠 Face recognition
* ✅ Automatic attendance marking
* 🕐 Date and time recording
* 🚫 Duplicate attendance prevention
* 📊 Attendance report
* 🔎 Student search
* 🖥️ Simple graphical user interface
* ⚠️ Unknown face detection
* 💾 CSV-based attendance storage

## 🛠️ Technologies Used

| Technology       | Purpose                        |
| ---------------- | ------------------------------ |
| Python           | Main programming language      |
| OpenCV           | Webcam and image processing    |
| face_recognition | Face detection and recognition |
| NumPy            | Numerical operations           |
| Pandas           | Attendance data handling       |
| Tkinter          | Graphical user interface       |
| CSV              | Attendance data storage        |

## 📂 Project Structure

```text
Face_Recognition_Attendance/
│
├── main.py
├── register.py
├── recognize.py
├── attendance.py
├── database.py
├── requirements.txt
│
├── dataset/
│   └── Student face images
│
├── encodings/
│   └── Face encodings
│
└── attendance/
    └── attendance.csv
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Face-Recognition-Attendance.git
```

### 2. Open the project

```bash
cd Face-Recognition-Attendance
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

For Windows:

```powershell
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available, install the main packages:

```bash
pip install opencv-python face-recognition numpy pandas
```

## ▶️ How to Run

Start the application using:

```bash
python main.py
```

## 📝 How to Use

### Step 1: Register Student

Enter:

* Student Name
* Student ID

The system opens the webcam and captures the student's face.

### Step 2: Start Attendance

Click **Start Attendance**.

The webcam detects faces and compares them with registered students.

### Step 3: Face Recognition

If the face matches a registered student, the system displays the student's:

* Name
* Student ID

### Step 4: Attendance

The system automatically records:

```text
Student ID
Student Name
Date
Time
Status
```

Example:

```text
Student ID: 25BCE11213
Student Name: Nitin Chahar
Date: 2026-09-01
Time: 09:15:24
Status: Present
```

## 🔐 Privacy & Security

Face images and attendance records may contain personal information.

For this reason:

* Do not upload real student face images to a public repository.
* Do not upload personal attendance CSV files.
* Keep the `dataset/` folder private.
* Keep generated face encodings private.
* Use `.gitignore` to prevent sensitive files from being uploaded.

Example `.gitignore`:

```gitignore
venv/
__pycache__/
dataset/
encodings/
attendance/*.csv
*.pyc
.env
```

## 🚀 Future Improvements

The project can be improved by adding:

* SQLite/MySQL database
* Admin login system
* Student dashboard
* Monthly attendance reports
* Excel/PDF report generation
* Email notifications
* Cloud database
* Mobile application
* Multiple camera support
* Improved recognition under different lighting conditions

## 🎓 Academic Use

This project can be used as a **college mini project / major project** for demonstrating concepts of:

* Artificial Intelligence
* Computer Vision
* Machine Learning
* Python Programming
* Database Management
* GUI Development

## 👨‍💻 Author

**Nitin Chahar**

Face Recognition Attendance System
Developed using Python and Computer Vision.

## 📄 License

This project is intended for educational and academic purposes.
