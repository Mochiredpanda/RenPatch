import flet as ft
from app.ui.theme import current_theme as theme

class ResultsScreen(ft.Container):
    def __init__(self, on_wizard_click, on_manual_click):
        super().__init__()
        self.on_wizard_click = on_wizard_click
        self.on_manual_click = on_manual_click
        self.expand = True
        self.padding = 32
        self.bgcolor = "white"
        
        # Data Placeholders
        self.files_scanned = 0
        self.issues_found = 0
        self.unique_chars = 0
        self.missing_chars = 0

    def update_stats(self, files, issues, unique, missing):
        self.files_scanned = files
        self.issues_found = issues
        self.unique_chars = unique
        self.missing_chars = missing
        
        # Rebuild table rows
        # TODO: A cleaner way would be to just update Control values if we kept references
        self.content = self._build_content()
        self.update()

    def build(self):
        self.content = self._build_content()
        return self

    def _build_content(self):
        return ft.Column(
            controls=[
                # Header
                ft.Container(
                    content=ft.Text("Scan Results", size=18, color="#2c3e50", weight=ft.FontWeight.BOLD),
                    border=ft.border.only(bottom=ft.BorderSide(2, "#3498db")),
                    padding=ft.padding.only(bottom=8),
                    width=float("inf")
                ),
                ft.Text("✓ Scan completed successfully", color="#27ae60", weight=ft.FontWeight.BOLD, size=13),
                ft.Container(height=12),
                
                # Stats Table
                ft.DataTable(
                    width=float("inf"),
                    bgcolor="white",
                    border=ft.border.all(1, "#bdc3c7"),
                    vertical_lines=ft.border.BorderSide(1, "#bdc3c7"),
                    horizontal_lines=ft.border.BorderSide(1, "#bdc3c7"),
                    columns=[
                        ft.DataColumn(ft.Text("Category", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Count", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                    ],
                    rows=[
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("Files Scanned")),
                            ft.DataCell(ft.Text(str(self.files_scanned))),
                            ft.DataCell(self._badge("Complete", "success")),
                        ]),
                         ft.DataRow(cells=[
                            ft.DataCell(ft.Text("Unique Characters")),
                            ft.DataCell(ft.Text(str(self.unique_chars))),
                            ft.DataCell(self._badge("Analyzed", "success")),
                        ]),
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("Missing Characters")),
                            ft.DataCell(ft.Text(str(self.missing_chars))),
                            ft.DataCell(self._badge("Needs Patching", "error") if self.missing_chars > 0 else self._badge("OK", "success")),
                        ]),
                    ]
                ),
                
                ft.Container(height=24),
                
                # Action Buttons
                ft.Text("Choose Action:", size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                ft.Row(
                    controls=[
                        self._build_action_card("✨", "Automatic Fix", "Let the wizard handle everything automatically", "#27ae60", self.on_wizard_click),
                        self._build_action_card("🔧", "Manual Configuration", "Advanced options with full control", "#3498db", self.on_manual_click),
                    ],
                    spacing=16
                )
            ],
            scroll=ft.ScrollMode.AUTO
        )

    def _badge(self, text, status):
        color = "#155724"
        bg = "#d4edda"
        border = "#c3e6cb"
        
        if status == "warning":
            color = "#856404"
            bg = "#fff3cd"
            border = "#ffeaa7"
        elif status == "error":
            color = "#721c24"
            bg = "#f8d7da"
            border = "#f5c6cb"
            
        return ft.Container(
            content=ft.Text(text, size=11, weight=ft.FontWeight.BOLD, color=color),
            bgcolor=bg,
            border=ft.border.all(1, border),
            border_radius=3,
            padding=ft.padding.symmetric(horizontal=8, vertical=2)
        )

    def _build_action_card(self, icon, title, subtitle, color, on_click):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(icon, size=36),
                    ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color="#2c3e50"),
                    ft.Text(subtitle, size=12, color="#7f8c8d", text_align=ft.TextAlign.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            width=200,
            padding=24,
            border=ft.border.all(2, "#95a5a6"),
            border_radius=4,
            bgcolor="white",
            on_click=on_click,
            on_hover=lambda e: self._on_card_hover(e, color),
            ink=True,
            data=color # Store color for hover event
        )

    def _on_card_hover(self, e, color):
        e.control.border = ft.border.all(2, color if e.data == "true" else "#95a5a6")
        e.control.bgcolor = "#f8f9fa" if e.data == "true" else "white"
        e.control.update()
