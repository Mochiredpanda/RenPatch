import flet as ft
from app.ui.theme import current_theme as theme
import os

class DirectoryScreen(ft.Container):
    def __init__(self, on_browse_click, on_directory_drop, on_start_scan_click, on_back_click=None, selected_path=None):
        super().__init__()
        self.on_browse_click = on_browse_click
        self.on_directory_drop = on_directory_drop # Keep signature consistent, even if unused mostly
        self.on_start_scan_click = on_start_scan_click
        self.on_back_click = on_back_click
        self.selected_path = selected_path
        self.expand = True
        self.padding = 32
        self.bgcolor = "white"
        
        # Initialize Controls for State Management
        self._init_controls()
        
        # Build initial content
        self.content = self._build_layout()

    def _init_controls(self):
        # Header Controls
        self.status_icon = ft.Text("📁", size=36)
        self.status_text = ft.Text("Click or Drag Folder Here", size=15, color="#2c3e50", weight=ft.FontWeight.BOLD)
        
        # Input Field
        self.path_input = ft.TextField(
             label="Or paste path here", 
             text_size=12,
             height=40,
             content_padding=10,
             on_change=self._manual_path_change,
             border_color="#bdc3c7"
        )
        
        # Picker Container
        self.picker_box = ft.Container(
            content=ft.Column(
                controls=[
                    self.status_icon,
                    self.status_text,
                    ft.Text("Select your Ren'Py project directory", size=12, color="#7f8c8d"),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6
            ),
            padding=ft.padding.symmetric(vertical=40, horizontal=30),
            border=ft.border.all(2, "#95a5a6"),
            border_radius=4,
            bgcolor="white",
            on_click=self.on_browse_click,
            ink=True,
        )
        
        # Scan Button
        self.scan_btn = ft.Container(
            content=ft.Text("Begin Scanning", color=theme.colors.button_text, weight=ft.FontWeight.BOLD),
            padding=ft.padding.symmetric(horizontal=28, vertical=10),
            bgcolor="#bdc3c7", # Default disabled color
            # Gradient is None by default
            gradient=None,
            border=ft.border.all(1, "#95a5a6"),
            border_radius=4,
            on_click=self.on_start_scan_click,
            disabled=True,
            opacity=0.5,
            alignment=ft.alignment.center,
            width=200
        )
        
        # Apply initial state if path exists
        if self.selected_path:
            self.set_path(self.selected_path)

    def _build_layout(self):
        # Header Row
        header_row = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Select Project Directory", size=18, color="#2c3e50", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            width=50, height=3, bgcolor="#3498db", border_radius=1, margin=ft.margin.only(top=4)
                        )
                    ],
                    spacing=0
                ),
                ft.TextButton(
                    "Back", 
                    icon="arrow_back", 
                    on_click=self.on_back_click,
                    visible=bool(self.on_back_click)
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        return ft.Column(
            controls=[
                header_row,
                ft.Text("Choose the folder containing your Ren'Py game package files.", color="#7f8c8d", size=13),
                ft.Container(height=24),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self.picker_box, 
                            ft.Container(height=10),
                            self.path_input,
                            ft.Container(height=20),
                            self.scan_btn
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    expand=True,
                    alignment=ft.alignment.center
                )
            ]
        )

    def set_path(self, path):
        """Updates UI elements based on a valid directory path"""
        self.selected_path = path
        
        # Update Picker Box
        self.status_icon.value = "✅"
        self.status_text.value = os.path.basename(path)
        self.picker_box.border = ft.border.all(2, "#27ae60")
        self.picker_box.bgcolor = "#e8f8f0"
        
        # Update Input (if not user typing)
        if self.path_input.value != path:
             self.path_input.value = path
        
        # Update Button
        self.scan_btn.bgcolor = theme.colors.button_gradient_end
        self.scan_btn.gradient = ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[theme.colors.button_gradient_start, theme.colors.button_gradient_end]
        )
        self.scan_btn.border = ft.border.all(1, theme.colors.button_border)
        self.scan_btn.disabled = False
        self.scan_btn.opacity = 1.0
        
        # Call updates if mounted
        try:
            self.update()
        except:
            pass

    def _manual_path_change(self, e):
        path = e.control.value.strip()
        if os.path.isdir(path):
            self.set_path(path)
