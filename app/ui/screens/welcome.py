import flet as ft
from app.ui.theme import current_theme as theme

class WelcomeScreen(ft.Container):
    def __init__(self, on_start_click):
        super().__init__()
        self.on_start_click = on_start_click
        self.expand = True
        self.padding = 32
        self.bgcolor = "white"
        
    def build(self):
        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Image(src="icons/favicon.png", width=200, height=200),
                    margin=ft.margin.only(bottom=16)
                ),
                ft.Text(
                    "Welcome to RedPanda RenPatch", 
                    size=24, 
                    color="#2c3e50", 
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "Scan your Ren'Py project, find missing characters in your scripts.\nLet us take over from there.", 
                    color="#7f8c8d",
                    text_align=ft.TextAlign.CENTER,
                    size=14
                ),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Text("Start New Scan", color=theme.colors.button_text, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.symmetric(horizontal=28, vertical=10),
                    bgcolor=theme.colors.button_gradient_end,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_center,
                        end=ft.alignment.bottom_center,
                        colors=[theme.colors.button_gradient_start, theme.colors.button_gradient_end]
                    ),
                    border=ft.border.all(1, theme.colors.button_border),
                    border_radius=4,
                    on_click=self.on_start_click,
                    shadow=ft.BoxShadow(blur_radius=4, color="#33000000", offset=ft.Offset(0, 2)),
                    ink=True,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
