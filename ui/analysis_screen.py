import customtkinter as ctk
import cv2
import time
from ui.theme import LAVENDER, DEEP_PURPLE, HOT_PINK, ELECTRIC_BLUE, WHITE, MUTED_PURPLE, FONTS, DARK, NEON_LIME
from logic.cv_analyzer import analyze_stains, analyze_tears, analyze_wrinkles, calculate_final_grade

class AnalysisScreen(ctk.CTkToplevel):
    def __init__(self, master, image_bgr, on_complete):
        super().__init__(master)
        self.title("AI Defect Analysis")
        self.geometry("500x550")
        self.configure(fg_color=DARK)
        self.grab_set()

        self.image_bgr = image_bgr
        self.on_complete = on_complete

        # Run Analysis
        _, _, self.stain_risk = analyze_stains(self.image_bgr)
        _, _, self.tear_risk = analyze_tears(self.image_bgr)
        _, _, self.wrinkle_risk = analyze_wrinkles(self.image_bgr)
        self.final_grade, self.condition = calculate_final_grade(self.stain_risk, self.tear_risk, self.wrinkle_risk)

        self._build_ui()

    def _build_ui(self):
        # Body
        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.body, text="Final Assessment", font=("Outfit", 24, "bold"), text_color=WHITE).pack(pady=20)
        
        # Grid of results
        grid = ctk.CTkFrame(self.body, fg_color="transparent")
        grid.pack(pady=20)
        
        def add_row(parent, label, risk):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=8)
            ctk.CTkLabel(row, text=label, font=FONTS["body"], text_color=MUTED_PURPLE, width=150, anchor="e").pack(side="left", padx=10)
            
            color = "#C83B4C" if risk == "High risk" else ("#D19B26" if risk == "Medium risk" else "#217D49")
            pill = ctk.CTkFrame(row, fg_color=color, corner_radius=10)
            pill.pack(side="left", padx=10)
            ctk.CTkLabel(pill, text=risk, text_color=WHITE, font=FONTS["small"]).pack(padx=10, pady=2)

        add_row(grid, "Stain Detection:", self.stain_risk)
        add_row(grid, "Tear Detection:", self.tear_risk)
        add_row(grid, "Wrinkle Score:", self.wrinkle_risk)
        
        # Final Grade
        ctk.CTkFrame(self.body, fg_color=MUTED_PURPLE, height=1, width=300).pack(pady=30)
        
        ctk.CTkLabel(self.body, text="Calculated Condition Grade:", font=FONTS["small"], text_color=MUTED_PURPLE).pack()
        ctk.CTkLabel(self.body, text=self.final_grade, font=("Outfit", 32, "bold"), text_color=NEON_LIME).pack(pady=10)

        # Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", pady=20)
        
        ctk.CTkButton(footer, text="Use Photo & Grade", width=200, height=45,
                      fg_color=HOT_PINK, hover_color="#D4245F",
                      text_color=WHITE, font=FONTS["button"], corner_radius=12,
                      command=self._finish).pack(side="right", padx=30)
                      
        ctk.CTkButton(footer, text="Retake", width=120, height=45,
                      fg_color="transparent", border_width=1, border_color=MUTED_PURPLE,
                      text_color=MUTED_PURPLE, hover_color="#3A2D4A",
                      font=FONTS["button"], corner_radius=12,
                      command=self.destroy).pack(side="right", padx=10)

    def _finish(self):
        # Save image to unique path to pass back
        save_path = f"assets/uploads/capture_{int(time.time())}.jpg"
        cv2.imwrite(save_path, self.image_bgr)
        self.on_complete(save_path, self.condition)
        self.destroy()
