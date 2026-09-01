"""
gui.py
------
Main Tkinter GUI for the Face Recognition Attendance System.
Modern dark-themed layout with:
  - Register Student
  - Start Attendance
  - Attendance Report (with search)
  - Exit
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import cv2
from PIL import Image, ImageTk

from app.config import *
from app import database as db
from app import face_engine as fe


# ══════════════════════════════════════════════════════════════════════════════
#  Helper: Styled Button
# ══════════════════════════════════════════════════════════════════════════════

def styled_button(parent, text, command, width=22):
    """Create a consistent styled button matching the dark theme."""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=BTN_COLOR,
        fg=BTN_TEXT,
        font=FONT_BTN,
        width=width,
        relief=tk.FLAT,
        cursor="hand2",
        padx=10,
        pady=8,
        activebackground=BTN_HOVER,
        activeforeground=BTN_TEXT,
        bd=0
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOVER))
    btn.bind("<Leave>", lambda e: btn.config(bg=BTN_COLOR))
    return btn


# ══════════════════════════════════════════════════════════════════════════════
#  Register Student Window
# ══════════════════════════════════════════════════════════════════════════════

class RegisterWindow(tk.Toplevel):
    """Pop-up window for registering a new student with webcam capture."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Register New Student")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.grab_set()  # Make modal

        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Register New Student",
                 bg=BG_COLOR, fg=TITLE_COLOR, font=FONT_TITLE).pack(pady=(20, 10))

        form = tk.Frame(self, bg=BG_COLOR)
        form.pack(padx=30, pady=10)

        # Student Name
        tk.Label(form, text="Student Name:", bg=BG_COLOR, fg=TEXT_COLOR,
                 font=FONT_LABEL).grid(row=0, column=0, sticky="w", pady=6)
        self.name_var = tk.StringVar()
        tk.Entry(form, textvariable=self.name_var, font=FONT_LABEL,
                 bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                 width=24, relief=tk.FLAT, bd=5).grid(row=0, column=1, padx=10)

        # Student ID
        tk.Label(form, text="Student ID:", bg=BG_COLOR, fg=TEXT_COLOR,
                 font=FONT_LABEL).grid(row=1, column=0, sticky="w", pady=6)
        self.id_var = tk.StringVar()
        tk.Entry(form, textvariable=self.id_var, font=FONT_LABEL,
                 bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                 width=24, relief=tk.FLAT, bd=5).grid(row=1, column=1, padx=10)

        # Status label
        self.status_var = tk.StringVar(value="Fill in details and click 'Capture Faces'")
        tk.Label(self, textvariable=self.status_var, bg=BG_COLOR, fg=SUCCESS_COLOR,
                 font=FONT_SMALL, wraplength=380).pack(pady=8)

        # Progress bar
        self.progress = ttk.Progressbar(self, length=380, mode="determinate")
        self.progress.pack(pady=4)

        # Buttons
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(pady=14)
        styled_button(btn_frame, "📷  Capture Faces", self._start_capture, width=18).pack(side=tk.LEFT, padx=8)
        styled_button(btn_frame, "✖  Cancel", self.destroy, width=10).pack(side=tk.LEFT, padx=8)

    def _start_capture(self):
        name = self.name_var.get().strip()
        sid = self.id_var.get().strip()

        if not name or not sid:
            messagebox.showwarning("Missing Info", "Please enter both Name and Student ID.", parent=self)
            return

        # Guard duplicate IDs
        if db.student_id_exists(sid):
            messagebox.showerror("Duplicate ID",
                                 f"Student ID '{sid}' is already registered.\nUse a different ID.",
                                 parent=self)
            return

        self.status_var.set("Starting webcam…")
        self.progress["value"] = 0
        self.update()

        # Run capture in background thread to keep GUI responsive
        thread = threading.Thread(target=self._capture_thread, args=(sid, name), daemon=True)
        thread.start()

    def _capture_thread(self, sid, name):
        def update_progress(current, total):
            pct = (current / total) * 100
            self.progress["value"] = pct
            self.status_var.set(f"Capturing image {current} of {total}…")
            self.update_idletasks()

        def update_status(msg):
            self.status_var.set(msg)
            self.update_idletasks()

        # Step 1: Capture images
        success = fe.capture_student_images(sid, name, update_progress, update_status)

        if not success:
            self.status_var.set("❌ Capture failed. Please try again.")
            return

        # Step 2: Generate encodings
        update_status("⚙️  Generating face encodings (this may take a moment)…")
        fe.generate_encodings_for_student(sid, name, update_status)
        self.progress["value"] = 100


# ══════════════════════════════════════════════════════════════════════════════
#  Attendance Report Window
# ══════════════════════════════════════════════════════════════════════════════

class ReportWindow(tk.Toplevel):
    """Full attendance records table with search functionality."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Attendance Report")
        self.configure(bg=BG_COLOR)
        self.geometry("800x520")
        self.grab_set()

        self._build_ui()
        self._load_data()

    def _build_ui(self):
        tk.Label(self, text="Attendance Report",
                 bg=BG_COLOR, fg=TITLE_COLOR, font=FONT_TITLE).pack(pady=(15, 5))

        # Search bar
        search_frame = tk.Frame(self, bg=BG_COLOR)
        search_frame.pack(fill=tk.X, padx=20, pady=6)

        tk.Label(search_frame, text="🔍 Search:", bg=BG_COLOR,
                 fg=TEXT_COLOR, font=FONT_LABEL).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *a: self._load_data())
        tk.Entry(search_frame, textvariable=self.search_var, font=FONT_LABEL,
                 bg=PANEL_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                 width=28, relief=tk.FLAT, bd=5).pack(side=tk.LEFT, padx=10)

        styled_button(search_frame, "🔄  Refresh", self._load_data, width=12).pack(side=tk.RIGHT)

        # Treeview table
        cols = ("Student ID", "Student Name", "Date", "Time", "Status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=16)

        # Column widths
        widths = [100, 200, 110, 90, 90]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor=tk.CENTER)

        # Style the treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background=TABLE_ROW_ODD,
                         foreground=TEXT_COLOR,
                         fieldbackground=TABLE_ROW_ODD,
                         rowheight=26,
                         font=FONT_SMALL)
        style.configure("Treeview.Heading",
                         background=TABLE_HEADER,
                         foreground=TEXT_COLOR,
                         font=FONT_BOLD)
        style.map("Treeview", background=[("selected", ACCENT_COLOR)])

        self.tree.tag_configure("odd", background=TABLE_ROW_ODD)
        self.tree.tag_configure("even", background=TABLE_ROW_EVEN)

        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0), pady=10)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, pady=10)

        # Row count label
        self.count_var = tk.StringVar()
        tk.Label(self, textvariable=self.count_var, bg=BG_COLOR,
                 fg=WARNING_COLOR, font=FONT_SMALL).pack(pady=(0, 10))

    def _load_data(self, *_):
        query = self.search_var.get().strip() if hasattr(self, "search_var") else ""
        if query:
            df = db.search_student_attendance(query)
        else:
            df = db.load_attendance()

        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert rows with alternating colours
        for i, (_, row) in enumerate(df.iterrows()):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", tk.END, values=list(row), tags=(tag,))

        self.count_var.set(f"Total records: {len(df)}")


# ══════════════════════════════════════════════════════════════════════════════
#  Main App Window
# ══════════════════════════════════════════════════════════════════════════════

class AttendanceApp:
    """Main application class with sidebar navigation and status panel."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("900x580")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # Attendance thread control
        self._attendance_stop = threading.Event()
        self._attendance_thread = None

        ensure_directories()
        db.init_attendance_csv()

        self._build_ui()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Left sidebar ──────────────────────────────────────────────────────
        sidebar = tk.Frame(self.root, bg=PANEL_COLOR, width=230)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # App title / logo
        tk.Label(sidebar, text="🎓", bg=PANEL_COLOR, fg=TITLE_COLOR,
                 font=("Helvetica", 36)).pack(pady=(30, 4))
        tk.Label(sidebar, text="Attendance\nSystem", bg=PANEL_COLOR,
                 fg=TITLE_COLOR, font=FONT_TITLE, justify=tk.CENTER).pack()
        tk.Label(sidebar, text="Face Recognition", bg=PANEL_COLOR,
                 fg=TEXT_COLOR, font=FONT_SMALL).pack(pady=(0, 30))

        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=4)

        # Nav buttons
        buttons = [
            ("👤  Register Student", self._open_register),
            ("📷  Start Attendance", self._start_attendance),
            ("⛔  Stop Attendance", self._stop_attendance),
            ("📋  Attendance Report", self._open_report),
            ("🔍  Search Student", self._search_student),
        ]
        for text, cmd in buttons:
            styled_button(sidebar, text, cmd, width=22).pack(pady=5, padx=16)

        ttk.Separator(sidebar, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=12)
        styled_button(sidebar, "🚪  Exit", self._exit, width=22).pack(padx=16)

        # ── Right main panel ──────────────────────────────────────────────────
        main = tk.Frame(self.root, bg=BG_COLOR)
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Header
        header = tk.Frame(main, bg=ACCENT_COLOR, height=56)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="Face Recognition Attendance System",
                 bg=ACCENT_COLOR, fg=BTN_TEXT, font=FONT_TITLE).pack(side=tk.LEFT, padx=20, pady=12)

        # Camera preview area
        self.cam_label = tk.Label(main, bg="#0d0d1a",
                                  text="Camera feed will appear here\nwhen attendance is started",
                                  fg="#555577", font=FONT_LABEL,
                                  width=62, height=20)
        self.cam_label.pack(padx=20, pady=(16, 8))

        # Status panel
        status_frame = tk.Frame(main, bg=PANEL_COLOR)
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 12))

        tk.Label(status_frame, text="Status:", bg=PANEL_COLOR,
                 fg=WARNING_COLOR, font=FONT_BOLD).pack(side=tk.LEFT, padx=10, pady=8)
        self.status_var = tk.StringVar(value="Ready. Register students or start attendance.")
        tk.Label(status_frame, textvariable=self.status_var,
                 bg=PANEL_COLOR, fg=TEXT_COLOR, font=FONT_LABEL).pack(side=tk.LEFT, padx=4)

        # Today's count
        count_frame = tk.Frame(main, bg=BG_COLOR)
        count_frame.pack(fill=tk.X, padx=20)

        tk.Label(count_frame, text="Today's Attendance:", bg=BG_COLOR,
                 fg=TEXT_COLOR, font=FONT_LABEL).pack(side=tk.LEFT)
        self.today_count_var = tk.StringVar(value="0 students")
        tk.Label(count_frame, textvariable=self.today_count_var,
                 bg=BG_COLOR, fg=SUCCESS_COLOR, font=FONT_BOLD).pack(side=tk.LEFT, padx=8)

        self._refresh_today_count()

    # ── Actions ───────────────────────────────────────────────────────────────

    def _set_status(self, msg: str):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def _refresh_today_count(self):
        """Update today's attendance count display."""
        from datetime import datetime
        import pandas as pd
        df = db.load_attendance()
        today = datetime.now().strftime("%Y-%m-%d")
        count = len(df[df["Date"] == today]) if not df.empty else 0
        self.today_count_var.set(f"{count} student(s) marked today")
        self.root.after(5000, self._refresh_today_count)  # refresh every 5s

    def _open_register(self):
        RegisterWindow(self.root)

    def _start_attendance(self):
        if self._attendance_thread and self._attendance_thread.is_alive():
            messagebox.showinfo("Info", "Attendance is already running.", parent=self.root)
            return

        registered = db.get_all_students()
        if not registered:
            messagebox.showwarning("No Students",
                                   "No students registered yet.\nPlease register students first.",
                                   parent=self.root)
            return

        self._attendance_stop.clear()
        self._set_status("📷 Attendance started — looking for faces…")

        self._attendance_thread = threading.Thread(
            target=fe.run_attendance_recognition,
            kwargs={
                "on_recognized": self._on_recognized,
                "on_unknown": None,
                "on_frame": self._update_cam_feed,
                "stop_flag": self._attendance_stop
            },
            daemon=True
        )
        self._attendance_thread.start()

    def _stop_attendance(self):
        self._attendance_stop.set()
        self._set_status("⛔ Attendance stopped.")
        # Clear camera preview
        self.cam_label.config(image="",
                              text="Camera stopped.\nPress 'Start Attendance' to begin again.")

    def _on_recognized(self, sid: str, name: str, marked: bool):
        if marked:
            self._set_status(f"✅ Marked: {name} (ID: {sid})")
        else:
            self._set_status(f"ℹ️  {name} already marked today.")

    def _update_cam_feed(self, frame):
        """Convert OpenCV frame to Tkinter-compatible image and display it."""
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((640, 360))
            imgtk = ImageTk.PhotoImage(image=img)
            self.cam_label.config(image=imgtk, text="")
            self.cam_label.image = imgtk  # prevent garbage collection
        except Exception:
            pass

    def _open_report(self):
        ReportWindow(self.root)

    def _search_student(self):
        query = simpledialog.askstring(
            "Search Student",
            "Enter Student Name or ID:",
            parent=self.root
        )
        if query:
            ReportWindow(self.root)
            # Pre-fill search (ReportWindow opens fresh; user can type in it)
            self._set_status(f"🔍 Opened report. Search for: '{query}'")

    def _exit(self):
        self._attendance_stop.set()
        self.root.destroy()
