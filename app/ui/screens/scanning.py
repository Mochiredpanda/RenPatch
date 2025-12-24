import flet as ft
from app.ui.theme import current_theme as theme

class ScanningScreen(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 32
        self.bgcolor = "white"
        
        # UI Elements
        self.status_text = ft.Text("Initializing scanner...", color="#555555", size=12)
        self.progress_bar = ft.ProgressBar(width=400, color="#27ae60", bgcolor="#ecf0f1")

    def build(self):
        return ft.Column(
            controls=[
                ft.Container(
                    content=ft.ProgressRing(width=40, height=40, stroke_width=4, color="#3498db"),
                    margin=ft.margin.only(bottom=20)
                ),
                ft.Text("Scanning Project Files...", size=20, color="#2c3e50", weight=ft.FontWeight.BOLD),
                ft.Text("Please wait while we analyze your RenPy game", color="#7f8c8d", size=13),
                ft.Container(height=24),
                
                # Progress Bar Container
                ft.Container(
                    content=self.progress_bar,
                    padding=2,
                    border=ft.border.all(1, "#95a5a6"),
                    border_radius=3,
                    bgcolor="white",
                    shadow=ft.BoxShadow(blur_radius=3, color="#1A000000", offset=ft.Offset(0, 1), blur_style=ft.ShadowBlurStyle.INNER)
                ),
                
                ft.Container(height=8),
                self.status_text
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def set_status(self, text):
        self.status_text.value = text
        self.update()
        
    def set_progress(self, value):
        # Flet ProgressBar is indeterminate by default if value is None
        # But we can set it if we have concrete progress
        if value is not None:
             self.progress_bar.value = value
        self.update()

