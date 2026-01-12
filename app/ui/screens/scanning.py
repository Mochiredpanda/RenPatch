import flet as ft
from app.ui.theme import current_theme as theme
import math
import time
import threading

class ScanningScreen(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 32
        self.bgcolor = "white"
        
        # State
        self.is_animating = False
        
        # --- UI Elements ---
        
        # Logo with Magnifier Animation
        self.logo_image = ft.Image(
            src="assets/icons/favicon.png",
            width=150,
            height=150,
            fit=ft.ImageFit.CONTAIN,
            opacity=0.8
        )
        
        # Magnifier Icon
        # We will move this in a circle
        self.magnifier = ft.Icon("search", size=40, color="#3498db")
        self.magnifier_container = ft.Container(
            content=self.magnifier,
            width=40, height=40,
            # Start position (relative to stack)
            top=55, left=55,
            animate_position=300 # Smooth transition
        )
        
        # Animation Container (Stack)
        self.animation_stack = ft.Stack(
            controls=[
                self.logo_image,
                self.magnifier_container
            ],
            width=150,
            height=150,
        )

        self.status_text = ft.Text("Initializing...", color="#555555", size=14)
        self.file_path_text = ft.Text("", color="#95a5a6", size=11, italic=True)
        self.percentage_text = ft.Text("0%", color="#3498db", weight=ft.FontWeight.BOLD)
        
        self.progress_bar = ft.ProgressBar(width=500, color="#3498db", bgcolor="#ecf0f1", value=0)
        
        # Build layout
        self.content = self.build()

    def build(self):
        content = ft.Column(
            controls=[
                # Top Spacer
                ft.Container(expand=True),
                
                # Animation
                ft.Container(
                    content=self.animation_stack,
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(bottom=40)
                ),
                
                # Headings
                ft.Text("Scanning Project", size=24, color="#2c3e50", weight=ft.FontWeight.BOLD),
                ft.Text("Analyzing script files for characters...", color="#7f8c8d", size=14),
                
                ft.Container(height=30),
                
                # Progress Section
                ft.Row(
                    [self.status_text, self.percentage_text],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=500
                ),
                ft.Container(
                    content=self.progress_bar,
                    border_radius=4,
                    bgcolor="white",
                ),
                ft.Container(height=5),
                ft.Container(
                    content=self.file_path_text,
                    width=500,
                    alignment=ft.alignment.center_right
                ),
                
                # Bottom Spacer
                ft.Container(expand=True),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        return content

    def did_mount(self):
        self.is_animating = True
        # Start a thread for the looping animation so we don't block
        threading.Thread(target=self._animate_magnifier, daemon=True).start()

    def will_unmount(self):
        self.is_animating = False

    def _animate_magnifier(self):
        """Moves the magnifier in a circle"""
        center_x = 55 # Center of 150x150 minus half icon size (20) -> 75 - 20 = 55
        center_y = 55
        radius = 30
        angle = 0
        
        while self.is_animating:
            # Calculate new position
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            
            self.magnifier_container.left = x
            self.magnifier_container.top = y
            
            # Use page.update() if possible, but safely inside a try/catch in case page is gone
            try:
                self.magnifier_container.update() 
            except:
                break
            
            angle = (angle + 10) % 360
            time.sleep(0.05) 

    def set_status(self, text, filepath=""):
        self.status_text.value = text
        if filepath:
            # Truncate if too long
            if len(filepath) > 60:
                filepath = "..." + filepath[-57:]
            self.file_path_text.value = filepath
        self.update()
        
    def set_progress(self, value):
        if value is not None:
             self.progress_bar.value = value
             self.percentage_text.value = f"{int(value * 100)}%"
        self.update()

