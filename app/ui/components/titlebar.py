import flet as ft
from app.ui.theme import current_theme as theme

class TitleBar(ft.UserControl):
    def __init__(self, title="RenPatch Package Scanner & Patcher", on_close=None, on_minimize=None):
        super().__init__()
        self.title_text = title
        self.on_close = on_close
        
    def build(self):
        return ft.Container(
            content=ft.Row(
                controls=[
                    # Title
                    ft.Row(
                        controls=[
                            ft.Text("🎮", size=16),
                            ft.Text(self.title_text, size=13, color=theme.colors.title_bar_text),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8
                    ),
                    # Window Controls (Fake for now, but actionable)
                    ft.Row(
                        controls=[
                            self._build_window_btn("_", self.minimize_window),
                            self._build_window_btn("□", None), # Maximize disabled for fixed size
                            self._build_window_btn("×", self.close_window),
                        ],
                        spacing=2
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[theme.colors.title_bar_gradient_start, theme.colors.title_bar_gradient_end],
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border=ft.border.only(bottom=ft.BorderSide(1, theme.colors.title_bar_border)),
        )

    def _build_window_btn(self, text, on_click):
        return ft.Container(
            content=ft.Text(text, size=14, color="white", weight=ft.FontWeight.BOLD),
            width=28,
            height=24,
            bgcolor="#5a9de5",
            border=ft.border.all(1, "#357abd"),
            border_radius=2,
            alignment=ft.alignment.center,
            on_click=on_click,
            ink=True
        )

    def close_window(self, e):
        e.page.window_close()

    def minimize_window(self, e):
        e.page.window_minimized = True
        e.page.update()
