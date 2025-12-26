import flet as ft
from app.ui.theme import current_theme as theme
import os

class FontTable(ft.DataTable):
    def __init__(self, font_data_list, on_auto_fix_click, on_inspect_click):
        """
        font_data_list: List of dictionaries/objects containing:
          - file_path
          - role (Dialogue, UI, Unknown)
          - missing_count
          - total_chars
        """
        super().__init__(
            columns=[
                ft.DataColumn(ft.Text("Font File", weight="bold")),
                ft.DataColumn(ft.Text("Role")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Missing")),
                ft.DataColumn(ft.Text("Action")),
            ],
            border=ft.border.all(1, theme.colors.border),
            border_radius=4,
            vertical_lines=ft.border.BorderSide(1, "#f0f0f0"),
            horizontal_lines=ft.border.BorderSide(1, "#f0f0f0"),
            heading_row_color="#f8f9fa",
            data_row_color={"hovered": "#f1f2f6"},
            expand=True,
            column_spacing=20
        )
        self.font_data_list = font_data_list
        self.on_auto_fix_click = on_auto_fix_click
        self.on_inspect_click = on_inspect_click
        self._build_rows()

    def _build_rows(self):
        self.rows = []
        for font in self.font_data_list:
            filename = os.path.basename(font['file_path'])
            missing = font['missing_count']
            role = font['role']
            
            # Status Logic
            if missing == 0:
                status_icon = ft.Icon("check_circle", color="green", size=16)
                status_text = "Perfect"
                status_color = "green"
            elif missing < 50:
                status_icon = ft.Icon("warning_amber_rounded", color="orange", size=16) 
                status_text = "Minor"
                status_color = "orange"
            else:
                status_icon = ft.Icon("error_outline", color="red", size=16)
                status_text = "Critical"
                status_color = "red"

            # Action Buttons
            actions = ft.Row(
                controls=[
                    ft.IconButton(
                        icon="auto_fix_high", 
                        tooltip="Auto Fix (Wizard)",
                        icon_color=theme.colors.button_gradient_end,
                        on_click=lambda e, f=font: self.on_auto_fix_click(f)
                    ),
                    ft.IconButton(
                        icon="list_alt", 
                        tooltip="Inspect Details",
                        icon_color="#95a5a6",
                        on_click=lambda e, f=font: self.on_inspect_click(f)
                    )
                ],
                spacing=0
            )

            self.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row([
                                ft.Icon("font_download", size=16, color="#7f8c8d"),
                                ft.Text(filename, size=12, weight="bold")
                            ], spacing=8)
                        ),
                        ft.DataCell(ft.Text(role, size=12)),
                        ft.DataCell(ft.Row([status_icon, ft.Text(status_text, color=status_color, size=12)], spacing=4)),
                        ft.DataCell(ft.Text(f"{missing} chars", size=12, color=status_color if missing > 0 else "black")),
                        ft.DataCell(actions),
                    ]
                )
            )
