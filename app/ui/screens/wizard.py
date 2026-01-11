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
        self.donor_font_path = None
        self.scan_data = None
        
        # UI Elements
        self.header = ft.Text("Patch Wizard", size=24, weight=ft.FontWeight.BOLD, color=theme.colors.text_primary)
        self.description = ft.Text("Create a lightweight patch font to fill in missing characters.", size=14, color=theme.colors.text_secondary)
        
        self.target_info = ft.Text("Target: None", size=16, weight=ft.FontWeight.BOLD)
        self.missing_count = ft.Text("Missing: 0", size=14, color=theme.colors.error)
        
        self.donor_path_text = ft.Text("No font selected", size=12, italic=True)
        self.file_picker = ft.FilePicker(on_result=self.on_donor_file_picked)
        
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
                
                # Donor Section
                ft.Container(
                    content=ft.Column([
                        ft.Text("2. Donor Font (Source)", weight="bold", color=theme.colors.text_primary),
                        ft.Text("Select a full font (e.g. SourceHanSansSC-Regular.otf) to extract characters from.", size=12, color=theme.colors.text_secondary),
                        ft.Row([
                            ft.ElevatedButton(
                                "Select File", 
                                icon="folder_open", 
                                on_click=lambda _: self.file_picker.pick_files(allowed_extensions=["ttf", "otf"]),
                                style=ft.ButtonStyle(
                                    color=theme.colors.button_text,
                                    bgcolor={"": theme.colors.button_gradient_end},
                                    shape=ft.RoundedRectangleBorder(radius=4),
                                )
                            ),
                            self.donor_path_text
                        ]),
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

    def set_data(self, target_font_data, scan_data):
        self.target_font_data = target_font_data
        self.scan_data = scan_data
        
        # Reset UI
        self.target_info.value = f"Target: {os.path.basename(target_font_data['file_path'])}"
        self.missing_count.value = f"Missing Characters: {target_font_data['missing_count']}"
        self.donor_path_text.value = "No font selected"
        self.donor_font_path = None
        self.patch_btn.disabled = True
        self.log_view.controls.clear()
        self.progress_bar.value = 0
        self.status_text.value = "Ready to patch."
        
        if hasattr(self, "page") and self.page:
            self.page.overlay.append(self.file_picker)
            self.page.update()

    def on_donor_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files:
            file_path = e.files[0].path
            self.donor_font_path = file_path
            self.donor_path_text.value = os.path.basename(file_path)
            self.patch_btn.disabled = False
            self.page.update()

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
            self.log(f"Starting patch process...", "cyan")
            
            project_dir = self.scan_data["directory"]
            game_dir = os.path.join(project_dir, "game") # Assume standard structure
            if not os.path.exists(game_dir):
                 # Fallback if selected folder IS game/
                 if os.path.basename(project_dir) == "game":
                     game_dir = project_dir
                 else:
                     game_dir = project_dir # Last resort
            
            self.log(f"Output directory: {game_dir}")
            
            # 1. Generate Patch Font
            missing_chars = self.target_font_data["missing_set"]
            patch_font_path = os.path.join(game_dir, "patch.ttf")
            
            self.log(f"Generating subset font from {os.path.basename(self.donor_font_path)}...", "yellow")
            
            success, patched_chars, failed_chars = patcher.generate_patch_font(
                missing_chars, 
                self.donor_font_path, 
                patch_font_path
            )
            
            if success:
                self.log(f"Patch font created: patch.ttf ({len(patched_chars)} chars)", "green")
            else:
                self.log("Failed to create patch font.", "red")
                return

            # 2. Generate Script
            self.log("Generating Ren'Py integration script...", "yellow")
            script_path = os.path.join(game_dir, "renpatch_init.rpy")
            log_path = os.path.join(project_dir, "renpatch_log.json")
            
            lite_font_name = os.path.basename(self.target_font_data['file_path'])
            
            patcher.generate_renpy_script(
                patched_chars,
                failed_chars,
                "patch.ttf", # Relative path for Ren'Py
                lite_font_name, # Relative path (assuming it is in game or configured paths)
                script_path,
                log_path
            )
            
            self.log(f"Script created: renpatch_init.rpy", "green")
            
            if failed_chars:
                self.log(f"Warning: {len(failed_chars)} characters could not be found in donor font.", "orange")
            
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
