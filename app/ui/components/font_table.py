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
                ft.DataColumn(ft.Text("Font File", weight="bold", size=14, color="black")),
                ft.DataColumn(ft.Text("Role", weight="bold", size=14, color="black")),
                ft.DataColumn(ft.Text("Status", weight="bold", size=14, color="black")),
                ft.DataColumn(ft.Text("Missing", weight="bold", size=14, color="black")),
                ft.DataColumn(ft.Text("Action", weight="bold", size=14, color="black")),
            ],
            border=ft.border.all(1, "#bdc3c7"), # Darker border
            border_radius=4,
            vertical_lines=ft.border.BorderSide(1, "#dcdcdc"), # Darker lines
            horizontal_lines=ft.border.BorderSide(1, "#dcdcdc"), # Darker lines
            heading_row_color="#ecf0f1", # Slightly darker header background
            heading_row_height=40,
            data_row_color={"hovered": "#f1f2f6"},
            data_row_min_height=50, # More breathing room
            expand=True,
            column_spacing=30 # Increased spacing
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
            is_ui_role = role in ["UI", "UI/Symbols", "Name/UI"]
            
            if missing == 0:
                status_icon = ft.Icon("check_circle", color="green", size=16)
                status_text = "Perfect"
                status_color = "green"
            elif is_ui_role:
                # UI fonts are not expected to cover all dialogue chars
                status_icon = ft.Icon("info_outline", color="blue", size=16)
                status_text = "Safe (UI)"
                status_color = "blue"
            elif missing < 50:
                status_icon = ft.Icon("warning_amber_rounded", color="orange", size=16) 
                status_text = "Minor"
                status_color = "orange"
            else:
                status_icon = ft.Icon("error_outline", color="red", size=16)
                status_text = "Critical"
                status_color = "red"

            # Display missing count differently for UI roles
            missing_display_color = status_color if missing > 0 and not is_ui_role else "black"
            missing_text = f"{missing} chars"
            if is_ui_role and missing > 0:
                 missing_text = f"{missing} (Ignored)"
                 missing_display_color = "#95a5a6" # Greyed out

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
                                ft.Icon("font_download", size=18, color="#2c3e50"),
                                ft.Text(filename, size=14, weight="bold", color="black")
                            ], spacing=10)
                        ),
                        ft.DataCell(ft.Text(role, size=14, color="black")),
                        ft.DataCell(ft.Row([status_icon, ft.Text(status_text, color=status_color, size=14, weight=ft.FontWeight.W_500)], spacing=6)),
                        ft.DataCell(ft.Text(missing_text, size=14, color=missing_display_color)),
                        ft.DataCell(actions),
                    ]
                )
            )
