import flet as ft
from app.ui.theme import current_theme as theme
from app.ui.components.font_table import FontTable

class ResultsScreen(ft.Container):
    def __init__(self, on_wizard_click, on_manual_click):
        super().__init__()
        self.on_wizard_click = on_wizard_click
        self.on_manual_click = on_manual_click
        self.expand = True
        self.padding = 32
        self.bgcolor = "white"
        
        # Data Placeholders
        self.font_data = [] # List of dicts
        self.global_stats = {"files": 0, "unique_chars": 0}

    def update_data(self, global_stats, font_health_data):
        self.global_stats = global_stats
        self.font_data = font_health_data
        
        # Rebuild content with new data
        self.content = self._build_content()
        # self.update() # Removed to prevent error if not mounted yet

    def build(self):
        self.content = self._build_content()
        return self

    def _build_content(self):
        # Calculate summary
        total_fonts = len(self.font_data)
        critical_fonts = sum(1 for f in self.font_data if f['missing_count'] > 0)
        
        return ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Text("Font Health Dashboard", size=18, color="#2c3e50", weight=ft.FontWeight.BOLD),
                    border=ft.border.only(bottom=ft.BorderSide(2, "#3498db")),
                    padding=ft.padding.only(bottom=8),
                    width=float("inf")
                ),
                
                # Global Summary
                ft.Row(
                    controls=[
                        self._summary_card("Files Scanned", self.global_stats['files'], "#3498db"),
                        self._summary_card("Unique Chars", self.global_stats['unique_chars'], "#9b59b6"),
                        self._summary_card("Fonts Found", total_fonts, "#e67e22"),
                        self._summary_card("Issues Detected", critical_fonts, "#e74c3c" if critical_fonts > 0 else "#27ae60"),
                    ],
                    spacing=16
                ),
                
                ft.Container(height=24),
                
                ft.Text("Detected Fonts", size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                ft.Text("Select a font to patch or inspect its missing characters.", size=12, color="#7f8c8d"),
                
                # Font Table
                FontTable(
                    font_data_list=self.font_data,
                    on_auto_fix_click=self.on_wizard_click,
                    on_inspect_click=self.on_manual_click
                ) if self.font_data else ft.Container(
                    content=ft.Text("No fonts found in project directory.", italic=True, color="#95a5a6"),
                    padding=20,
                    alignment=ft.alignment.center
                ),
            ],
            scroll=ft.ScrollMode.AUTO
        )

    def _summary_card(self, label, value, color):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(str(value), size=20, weight="bold", color=color),
                    ft.Text(label, size=11, color="#7f8c8d")
                ],
                spacing=2
            ),
            bgcolor="#f8f9fa",
            border=ft.border.all(1, "#ecf0f1"),
            border_radius=4,
            padding=12,
            width=120
        )
