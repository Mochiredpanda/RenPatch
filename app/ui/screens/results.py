import flet as ft
from app.ui.theme import current_theme as theme
from app.ui.components.font_table import FontTable

class ResultsScreen(ft.Container):
    def __init__(self, on_wizard_click, on_manual_click, on_back_click=None):
        super().__init__()
        self.on_wizard_click = on_wizard_click
        self.on_manual_click = on_manual_click
        self.on_back_click = on_back_click
        self.expand = True
        self.padding = 32
        self.bgcolor = "white"
        self.alignment = ft.alignment.top_left # align container content to top left
        
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
        
        # Header Row with Back Button
        header_row = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Scan Results", size=18, color="#2c3e50", weight=ft.FontWeight.BOLD),
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
                #  ft.Row([
                #     ft.IconButton(icon="arrow_back", on_click=self.on_back_click, visible=bool(self.on_back_click)),
                #     ft.Text("Scan Results", size=18, color="#2c3e50", weight=ft.FontWeight.BOLD),
                #  ]),
                 # Placeholder for potential future actions
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        return ft.Column(
            controls=[
                # Header
                header_row,

                ft.Container(height=24),

                # Global Summary
                ft.Row(
                    controls=[
                        self._summary_card("Scripts Scanned", self.global_stats['files'], "#3498db"),
                        self._summary_card("Unique Chars", self.global_stats['unique_chars'], "#3498db"),
                        self._summary_card("Fonts Found", total_fonts, "#3498db"),
                        self._summary_card("Missing Chars", critical_fonts, "#e74c3c" if critical_fonts > 0 else "#3498db"),
                    ],
                    spacing=16,
                    # alignment=ft.MainAxisAlignment.START
                ),
                
                ft.Container(height=24),
                
                ft.Text("Detected Fonts", size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                ft.Text("Select a font to patch or inspect its missing characters.", size=12, color="#7f8c8d"),
                
                # Font Table
                ft.Container(height=16),

                # Font Table
                ft.Container(
                    content=FontTable(
                        font_data_list=self.font_data,
                        on_auto_fix_click=self.on_wizard_click,
                        on_inspect_click=self.on_manual_click
                    ) if self.font_data else ft.Container(
                        content=ft.Text("No fonts found in project directory.", italic=True, color="#95a5a6"),
                        padding=20,
                        alignment=ft.alignment.center
                    ),
                    margin=ft.margin.only(bottom=20)
                ),
                
                # Footer Explanation
                ft.Container(
                     content=ft.Column([
                         ft.Row([
                             ft.Icon("auto_fix_high", color=theme.colors.button_gradient_end, size=16),
                             ft.Text("Wizard Mode: Automatically generate a patch font + integration script.", size=12, color="#555555"),
                         ]),
                         ft.Row([
                             ft.Icon("list_alt", color="#95a5a6", size=16),
                             ft.Text("Manual Mode: Inspect missing characters list (Coming Soon).", size=12, color="#555555"),
                         ]),
                     ], spacing=8),
                     padding=20,
                     bgcolor="#f8f9fa",
                     border_radius=5,
                     border=ft.border.all(1, "#ecf0f1")
                ),
                
                ft.Container(height=40),
            ],
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            alignment=ft.MainAxisAlignment.START
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
