"""
Face Recognition Attendance System
===================================
Main entry point - imports and launches the GUI application.
"""

from app.gui import AttendanceApp
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
