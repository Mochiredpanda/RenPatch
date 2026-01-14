import flet as ft
from app.ui.theme import current_theme as theme
from app.core import patcher
import os
import threading

class WizardScreen(ft.Container):
    def __init__(self, on_back_click, on_patch_complete_click):
        super().__init__()
        self.on_back_click = on_back_click
        self.on_patch_complete_click = on_patch_complete_click
        self.expand = True
        self.padding = 32
        self.bgcolor = "white"
        
        # State
        self.target_font_data = None
        self.donor_fonts = [] # List of paths
        self.scan_data = None
        
        # UI Elements
        self.header = ft.Text("Patch Wizard", size=24, weight=ft.FontWeight.BOLD, color=theme.colors.text_primary)
        self.description = ft.Text("Create a lightweight patch font to fill in missing characters.", size=14, color=theme.colors.text_secondary)
        
        self.target_info = ft.Text("Target: None", size=16, weight=ft.FontWeight.BOLD)
        self.missing_count = ft.Text("Missing: 0", size=14, color=theme.colors.error)
        
        self.file_picker = ft.FilePicker(on_result=self.on_donor_file_picked)
        
        # Donor List View
        self.donor_list_view = ft.Column(spacing=5)
        
        self.log_view = ft.Column(scroll=ft.ScrollMode.AUTO, height=200)
        self.progress_bar = ft.ProgressBar(width=400, color=theme.colors.primary, bgcolor="#eeeeee", value=0)
        self.status_text = ft.Text("Ready", size=12)
        
        self.patch_btn = ft.ElevatedButton(
            "Generate Patch",
            icon="auto_fix_high",
            style=ft.ButtonStyle(
                color="white",
                bgcolor=theme.colors.button_gradient_end,
                shape=ft.RoundedRectangleBorder(radius=4),
            ),
            on_click=self.on_patch_click,
            disabled=True
        )

    def build(self):
        self.content = ft.Column(
            controls=[
                ft.Row([
                    ft.IconButton(icon="arrow_back", on_click=self.on_back_click),
                    self.header
                ]),
                self.description,
                ft.Divider(),
                
                # Info Section
                ft.Container(
                    content=ft.Column([
                        ft.Text("1. Target Font (Lite)", weight="bold", color=theme.colors.text_primary),
                        self.target_info,
                        self.missing_count,
                    ]),
                    padding=16,
                    bgcolor=theme.colors.panel_bg,
                    border=ft.border.all(1, theme.colors.panel_border),
                    border_radius=4
                ),
                
                ft.Container(height=16),
                
                # Donor Section (Multi-source)
                ft.Container(
                    content=ft.Column([
                        ft.Text("2. Donor Pool (Prioritized)", weight="bold", color=theme.colors.text_primary),
                        ft.Text("Add one or more fonts. The wizard will search them in order.", size=12, color=theme.colors.text_secondary),
                        
                        ft.Container(height=8),
                        
                        # List of added fonts
                        ft.Container(
                            content=self.donor_list_view,
                            bgcolor="white",
                            border=ft.border.all(1, "#f0f0f0"),
                            border_radius=4,
                            padding=10
                        ),
                        
                        ft.Container(height=8),
                        
                        ft.ElevatedButton(
                            "Add Font", 
                            icon="add", 
                            on_click=lambda _: self.file_picker.pick_files(allowed_extensions=["ttf", "otf"]),
                            style=ft.ButtonStyle(
                                color=theme.colors.button_text,
                                bgcolor={"": theme.colors.button_gradient_end},
                                shape=ft.RoundedRectangleBorder(radius=4),
                            )
                        ),
                    ]),
                    padding=16,
                    bgcolor=theme.colors.panel_bg,
                    border=ft.border.all(1, theme.colors.panel_border),
                    border_radius=4
                ),
                
                ft.Container(height=16),
                
                # Action Section
                ft.Container(
                    content=ft.Column([
                        ft.Text("3. Generate", weight="bold", color=theme.colors.text_primary),
                        self.patch_btn,
                        self.progress_bar,
                        self.status_text
                    ]),
                    padding=16,
                    bgcolor=theme.colors.panel_bg,
                    border=ft.border.all(1, theme.colors.panel_border),
                    border_radius=4
                ),
                
                # Log Section
                ft.Container(height=16),
                ft.Text("Log", weight="bold", size=12, color=theme.colors.text_secondary),
                ft.Container(
                    content=self.log_view,
                    bgcolor="black",
                    padding=10
                )
            ],
            scroll=ft.ScrollMode.AUTO
        )
        return self

    def set_data(self, font_data_list, scan_data):
        self.target_font_data = font_data_list[0] if font_data_list else None
        self.scan_data = scan_data
        
        if not self.target_font_data:
             self.target_info.value = "Target: No Fonts Found"
             self.missing_count.value = "Missing: 0"
             return

        # Reset UI
        self.target_info.value = f"Target: {os.path.basename(self.target_font_data['file_path'])} (Critical)"
        self.missing_count.value = f"Missing Characters: {self.target_font_data['missing_count']}"
        
        self.donor_fonts = []
        self._refresh_donor_list()
        
        self.patch_btn.disabled = True
        self.log_view.controls.clear()
        self.progress_bar.value = 0
        self.status_text.value = "Ready to patch."
        
        if hasattr(self, "page") and self.page:
            self.page.overlay.append(self.file_picker)
            self.page.update()

    def on_donor_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            for f in e.files:
                if f.path not in self.donor_fonts:
                    self.donor_fonts.append(f.path)
            
            self._refresh_donor_list()
            self.patch_btn.disabled = False
            self.page.update()
            
    def _refresh_donor_list(self):
        self.donor_list_view.controls.clear()
        
        if not self.donor_fonts:
            self.donor_list_view.controls.append(ft.Text("No fonts added yet.", italic=True, size=12, color="#95a5a6"))
        else:
            for i, font_path in enumerate(self.donor_fonts):
                filename = os.path.basename(font_path)
                
                row = ft.Row(
                    controls=[
                        ft.Icon("font_download", size=16, color="#7f8c8d"),
                        ft.Text(f"{i+1}. {filename}", size=12, weight="bold", expand=True),
                        ft.IconButton(
                            icon="close", 
                            icon_size=14, 
                            icon_color="red", 
                            tooltip="Remove",
                            on_click=lambda e, path=font_path: self._remove_donor(path)
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
                self.donor_list_view.controls.append(row)
        
        # Check generate button state
        self.patch_btn.disabled = len(self.donor_fonts) == 0
        if hasattr(self, "page") and self.page:
            self.page.update()

    def _remove_donor(self, path):
        if path in self.donor_fonts:
            self.donor_fonts.remove(path)
            self._refresh_donor_list()

    def log(self, message, color="white"):
        self.log_view.controls.append(ft.Text(message, color=color, size=12, font_family="Consolas"))
        if hasattr(self, "page"):
            self.page.update()

    def on_patch_click(self, e):
        self.patch_btn.disabled = True
        self.progress_bar.value = None # Indeterminate
        self.page.update()
        
        threading.Thread(target=self._run_patch_process, daemon=True).start()

    def _run_patch_process(self):
        try:
            self.log(f"Starting multi-source patch...", "cyan")
            
            project_dir = self.scan_data["directory"]
            game_dir = os.path.join(project_dir, "game") # Assume standard structure
            if not os.path.exists(game_dir):
                 # Fallback
                 if os.path.basename(project_dir) == "game":
                     game_dir = project_dir
                 else:
                     game_dir = project_dir # Last resort
            
            self.log(f"Output directory: {game_dir}")
            
            missing_chars = self.target_font_data["missing_set"]
            
            # 1. Generate Multiple Patches
            self.log(f"Searching for {len(missing_chars)} chars in {len(self.donor_fonts)} fonts...", "yellow")
            
            patches_list, failed_chars = patcher.generate_multi_patch(
                missing_chars, 
                self.donor_fonts, 
                game_dir
            )
            
            if patches_list:
                for p in patches_list:
                    self.log(f"Generated {p['filename']} from {p['source']} ({len(p['chars'])} chars)", "green")
            else:
                self.log("No patches could be generated.", "red")
                self.status_text.value = "Failed."
                return

            # 2. Generate Script
            self.log("Generating Ren'Py integration script...", "yellow")
            script_path = os.path.join(game_dir, "renpatch_init.rpy")
            log_path = os.path.join(project_dir, "renpatch_log.json")
            
            lite_font_name = os.path.basename(self.target_font_data['file_path'])
            
            patcher.generate_renpy_script(
                patches_list,
                failed_chars,
                lite_font_name, # Relative path (assuming it is in game or configured paths)
                script_path,
                log_path
            )
            
            self.log(f"Script created: renpatch_init.rpy", "green")
            
            if failed_chars:
                self.log(f"Warning: {len(failed_chars)} characters could not be found in any donor.", "orange")
            else:
                self.log("Success! All characters patched.", "green")
            
            self.status_text.value = "Patch Complete!"
            self.progress_bar.value = 1.0
            self.patch_btn.disabled = False
            
            if hasattr(self, "page"):
                self.page.update()
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.log(f"Error: {e}", "red")
            self.status_text.value = "Error occurred."
            self.patch_btn.disabled = False
            if hasattr(self, "page"):
                self.page.update()
