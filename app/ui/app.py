import flet as ft
from app.ui.theme import current_theme as theme
from app.ui.components.titlebar import TitleBar

class RenPatchApp(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.spacing = 0
        
        # Configure Window
        self.page.window_frameless = True # Custom Title Bar needs frameless
        self.page.window_bgcolor = "#00000000" # Transparent for custom corners if needed
        self.page.bgcolor = theme.colors.window_bg
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        
        # UI Components
        self.title_bar = TitleBar(on_minimize=self.minimize, on_close=self.close)
        
        self.sidebar = ft.Container(
            width=200,
            bgcolor=theme.colors.sidebar_bg,
            border=ft.border.only(right=ft.BorderSide(1, theme.colors.sidebar_border)),
            padding=ft.padding.symmetric(vertical=16, horizontal=8),
            content=ft.Column(
                controls=[
                    ft.Text("WORKFLOW", size=11, color="#555555", weight=ft.FontWeight.BOLD),
                    # TODO: Add Sidebar Items
                    self._build_sidebar_item("① Start", active=True),
                    self._build_sidebar_item("② Select Folder", disabled=True),
                    self._build_sidebar_item("③ Scan Project", disabled=True),
                    self._build_sidebar_item("④ View Results", disabled=True),
                    self._build_sidebar_item("⑤ Take Action", disabled=True),
                ],
                spacing=4
            )
        )
        
        self.content_area = ft.Container(
            expand=True,
            bgcolor=ft.colors.WHITE,
            padding=32,
            content=ft.Column(
                controls=[
                    ft.Text("Welcome to RenPy Scanner", size=24, color="#2c3e50", weight=ft.FontWeight.BOLD),
                    ft.Text("Scan your RenPy game projects for issues and automatically generate patches", color="#7f8c8d"),
                    ft.Container(height=40),
                    ft.ElevatedButton("Start New Scan", bgcolor="#3498db", color="white")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        self.controls = [
            # Main Window Container with Border
            ft.Container(
                expand=True,
                border=ft.border.all(1, theme.colors.border),
                bgcolor=theme.colors.window_bg,
                content=ft.Column(
                    controls=[
                        # Title Bar
                        self.title_bar,
                        
                        # Toolbar (Placeholder)
                        ft.Container(
                            height=40,
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.top_center,
                                end=ft.alignment.bottom_center,
                                colors=["#f5f5f5", "#e8e8e8"]
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, "#bbbbbb")),
                        ),
                        
                        # Body
                        ft.Container(
                            expand=True,
                            content=ft.Row(
                                controls=[
                                    self.sidebar,
                                    self.content_area
                                ],
                                spacing=0,
                                expand=True
                            )
                        )
                    ],
                    spacing=0,
                    expand=True
                )
            )
        ]

    def _build_sidebar_item(self, text, active=False, disabled=False):
        color = theme.colors.sidebar_text_active if active else theme.colors.sidebar_text
        bgcolor = theme.colors.sidebar_item_active if active else None
        opacity = 0.5 if disabled else 1.0
        
        return ft.Container(
            content=ft.Row([
                ft.Text(text, size=13, color=color, weight=ft.FontWeight.BOLD if active else ft.FontWeight.NORMAL)
            ]),
            padding=ft.padding.symmetric(vertical=8, horizontal=12),
            bgcolor=bgcolor,
            border_radius=3,
            opacity=opacity,
        )

    def minimize(self, e):
        self.page.window_minimized = True
        self.page.update()

    def close(self, e):
        self.page.window_close()
