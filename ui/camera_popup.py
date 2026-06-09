import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from ui.theme import LAVENDER, DEEP_PURPLE, HOT_PINK, WHITE, FONTS, MUTED_PURPLE
import threading

class CameraPopup(ctk.CTkToplevel):
    def __init__(self, master, on_capture):
        super().__init__(master)
        self.title("Scan with Camera")
        self.geometry("640x550")
        self.configure(fg_color=LAVENDER)
        self.grab_set()  # Make modal

        self.on_capture = on_capture
        self.cap = self._find_working_camera()
        self.is_running = True
        self.current_frame = None

        self._build_ui()
        self._update_feed()

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _find_working_camera(self):
        # Try finding a working camera by testing indices 0, 1, 2
        for idx in range(3):
            cap = cv2.VideoCapture(idx)
            if cap.isOpened():
                # Test if we can actually read a frame
                ret, _ = cap.read()
                if ret:
                    return cap
                cap.release()
        
        # If CAP_ANY fails, try CAP_DSHOW for Windows
        for idx in range(3):
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    return cap
                cap.release()
                
        # Return a fallback capture object (even if it's dead)
        return cv2.VideoCapture(0)


    def _build_ui(self):
        ctk.CTkLabel(self, text="Scan Item for Defects",
                     font=("Outfit", 24, "bold"),
                     text_color=DEEP_PURPLE).pack(pady=(20, 10))

        self.video_label = ctk.CTkLabel(self, text="")
        self.video_label.pack(pady=10, padx=20)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.capture_btn = ctk.CTkButton(btn_frame, text="Capture 📸", width=150, height=40,
                      fg_color=HOT_PINK, hover_color="#D4245F",
                      text_color=WHITE, font=FONTS["button"], corner_radius=12,
                      command=self._capture_image)
        self.capture_btn.pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame, text="Cancel", width=100, height=40,
                      fg_color="transparent", border_width=1, border_color=MUTED_PURPLE,
                      text_color=MUTED_PURPLE, hover_color="#E0D4EB",
                      font=FONTS["button"], corner_radius=12,
                      command=self._on_closing).pack(side="left", padx=10)

    def _update_feed(self):
        if not self.is_running:
            return

        ret, frame = self.cap.read()
        if not ret or frame is None:
            # Fallback for systems without a working webcam
            import numpy as np
            frame = np.ones((480, 640, 3), dtype=np.uint8) * 220
            # Draw a mock "shirt"
            cv2.circle(frame, (320, 240), 150, (180, 150, 150), -1)
            # Draw a mock "stain"
            cv2.circle(frame, (360, 260), 25, (100, 80, 80), -1)
            cv2.putText(frame, "No Camera Detected - Mock Feed", (80, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            ret = True

        if ret:
            self.current_frame = frame
            
            # Convert BGR to RGB
            cv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(cv_img)
            
            # Resize for display
            pil_img.thumbnail((580, 400))
            
            # Convert to CTkImage
            ctk_img = ctk.CTkImage(light_image=pil_img, size=pil_img.size)
            self.video_label.configure(image=ctk_img)
            self.video_label.image = ctk_img

        # Schedule next update
        self.after(30, self._update_feed)

    def _capture_image(self):
        if self.current_frame is not None:
            self.capture_btn.configure(state="disabled")
            self._countdown(3)

    def _countdown(self, count):
        if count > 0:
            self.capture_btn.configure(text=f"Capturing in {count}...")
            self.after(1000, self._countdown, count - 1)
        else:
            self.is_running = False
            self.cap.release()
            # Pass the BGR OpenCV frame to callback
            self.on_capture(self.current_frame)
            self.destroy()

    def _on_closing(self):
        self.is_running = False
        if self.cap.isOpened():
            self.cap.release()
        self.destroy()
