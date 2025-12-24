import flet as ft
from app.ui.theme import current_theme as theme

class DirectoryScreen(ft.Container):
    def __init__(self, on_browse_click, on_start_scan_click, on_back_click=None, selected_path=None):
        super().__init__()
        self.on_browse_click = on_browse_click
        self.on_start_scan_click = on_start_scan_click
        self.on_back_click = on_back_click
        self.selected_path = selected_path
        self.expand = True
        self.padding = 32
        self.bgcolor = "white"

    def build(self):
        # Header Row with Back Button
        header_row = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Select Project Directory", size=18, color="#2c3e50", weight=ft.FontWeight.BOLD),
                        ft.Container(
                            width=50, 
                            height=3, 
                            bgcolor="#3498db", 
                            border_radius=1, 
                            margin=ft.margin.only(top=4)
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

        header = ft.Column(
            controls=[
                header_row,
                ft.Text("Choose the folder containing your Ren'Py game package files.", color="#7f8c8d", size=13),
                ft.Container(height=24) # Padding requested by user
            ],
            spacing=8
        )

        # File Picker Area
        picker_content = ft.Column(
            controls=[
                ft.Text("✅" if self.selected_path else "📁", size=36),
                ft.Text(
                    self.selected_path if self.selected_path else "Click to Browse...", 
                    size=15, 
                    color="#2c3e50", 
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "Selected Directory" if self.selected_path else "Select your Ren'Py project directory", 
                    size=12, 
                    color="#7f8c8d"
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6
        )

        picker_box = ft.Container(
            content=picker_content,
            padding=ft.padding.symmetric(vertical=40, horizontal=30),
            border=ft.border.all(2, "#27ae60" if self.selected_path else "#95a5a6"),
            border_radius=4,
            bgcolor="#e8f8f0" if self.selected_path else "white",
            on_click=self.on_browse_click,
            ink=True,
            
            margin=ft.margin.only(bottom=20)
        )

        # Action Button
        scan_btn = ft.Container(
            content=ft.Text("Begin Scanning", color=theme.colors.button_text, weight=ft.FontWeight.BOLD),
            padding=ft.padding.symmetric(horizontal=28, vertical=10),
            bgcolor=theme.colors.button_gradient_end if self.selected_path else "#bdc3c7",
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[theme.colors.button_gradient_start, theme.colors.button_gradient_end]
            ) if self.selected_path else None,
            border=ft.border.all(1, theme.colors.button_border if self.selected_path else "#95a5a6"),
            border_radius=4,
            on_click=self.on_start_scan_click,
            disabled=not self.selected_path,
            opacity=1.0 if self.selected_path else 0.5,
            alignment=ft.alignment.center,
            width=200
        )

        self.content = ft.Column(
            controls=[
                header,
                ft.Container(
                    content=ft.Column(
                        controls=[picker_box, scan_btn],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    expand=True,
                    alignment=ft.alignment.center
                )
            ]
        )
