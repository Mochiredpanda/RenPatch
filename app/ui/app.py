import flet as ft
import time
import threading
from app.ui.theme import current_theme as theme

# Import Core Logic
from app.core import scanner, patcher
import os

# Import Screens
from app.ui.screens.welcome import WelcomeScreen
from app.ui.screens.directory import DirectoryScreen
from app.ui.screens.scanning import ScanningScreen
from app.ui.screens.results import ResultsScreen

class RenPatchApp(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.spacing = 0
        
        # Configure Window - System Frame Enabled
        self.page.window_frameless = False # Enabled system title bar
        # self.page.window_bgcolor = "#00000000" # Not needed for system frame
        self.page.bgcolor = theme.colors.window_bg
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        self.page.title = "RedPanda RenPatch" # Set Window Title
        self.page.window_icon = "icons/favicon.png" # Attempt to set window/dock icon
        
        # Initialize FilePicker
        self.file_picker = ft.FilePicker(on_result=self.on_directory_selected)
        self.page.overlay.append(self.file_picker)
        
        # Initialize Screens
        self.screens = {
            "welcome": WelcomeScreen(on_start_click=lambda e: self.navigate_to("directory")),
            "directory": DirectoryScreen(
                on_browse_click=lambda e: self.file_picker.get_directory_path(),
                on_start_scan_click=self.start_scanning,
                on_back_click=lambda e: self.navigate_to("welcome")
            ),
            "scanning": ScanningScreen(),
            "results": ResultsScreen(
                on_wizard_click=lambda e: print("Wizard clicked"),
                on_manual_click=lambda e: print("Manual clicked")
            )
        }
        
        self.current_screen = "welcome"
        
        # Sidebar setup
        self.sidebar_content = ft.Column(
            controls=[
                ft.Text("WORKFLOW", size=11, color="#555555", weight=ft.FontWeight.BOLD),
                self._build_sidebar_item("① Start", "welcome"),
                self._build_sidebar_item("② Select Folder", "directory"),
                self._build_sidebar_item("③ Scan Project", "scanning"),
                self._build_sidebar_item("④ View Results", "results"),
                self._build_sidebar_item("⑤ Take Action", "action", disabled=True),
            ],
            spacing=4
        )
        
        self.sidebar = ft.Container(
            width=200,
            bgcolor=theme.colors.sidebar_bg,
            border=ft.border.only(right=ft.BorderSide(1, theme.colors.sidebar_border)),
            padding=ft.padding.symmetric(vertical=16, horizontal=8),
            content=self.sidebar_content
        )
        
        self.content_area = ft.Container(
            expand=True,
            bgcolor="white",
            content=self.screens["welcome"] # Initial screen
        )

        # Removed TitleBar and Top Container
        self.controls = [
            ft.Container(
                expand=True,
                # border=ft.border.all(1, theme.colors.border), # No border needed for system window
                bgcolor=theme.colors.window_bg,
                content=ft.Row(
                    controls=[
                        self.sidebar,
                        self.content_area
                    ],
                    spacing=0,
                    expand=True
                )
            )
        ]

    def _build_sidebar_item(self, text, screen_id, disabled=False):
        # We need to access this dynamically later to update visual state
        # For simplicity in this iteration, we rebuild sidebar on nav
        active = (screen_id == self.current_screen)
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
            data=screen_id # Store ID
        )
        
    def navigate_to(self, screen_id):
        self.current_screen = screen_id
        self.content_area.content = self.screens[screen_id]
        
        # Refresh Sidebar
        self.sidebar_content.controls = [
            ft.Text("WORKFLOW", size=11, color="#555555", weight=ft.FontWeight.BOLD),
            self._build_sidebar_item("① Start", "welcome"),
            self._build_sidebar_item("② Select Folder", "directory"),
            self._build_sidebar_item("③ Scan Project", "scanning", disabled=(screen_id not in ["scanning", "results", "action"])),
            self._build_sidebar_item("④ View Results", "results", disabled=(screen_id not in ["results", "action"])),
            self._build_sidebar_item("⑤ Take Action", "action", disabled=(screen_id != "action")),
        ]
        
        self.update()

    def on_directory_selected(self, e: ft.FilePickerResultEvent):
        if e.path:
            # Update Directory Screen State
            dir_screen = self.screens["directory"]
            dir_screen.selected_path = e.path
            # Force rebuild of directory screen inner content
            dir_screen.content = dir_screen.build().content 
            dir_screen.update()

    def start_scanning(self, e):
        self.navigate_to("scanning")
        # Run in thread to not block UI
        threading.Thread(target=self._run_scan, args=(self.screens["directory"].selected_path,), daemon=True).start()
        
    def _run_scan(self, directory):
        scan_screen = self.screens["scanning"]
        
        try:
            # 1. Scanning Files
            scan_screen.set_status("Scanning Ren'Py script files...")
            scan_screen.set_progress(0.1)
            time.sleep(0.5) # UI pacing
            
            unique_chars = scanner.get_unique_characters(directory)
            scan_screen.set_status(f"Found {len(unique_chars)} unique characters...")
            scan_screen.set_progress(0.5)
            
            # 2. Font Analysis
            scan_screen.set_status("Analyzing fonts...")
            
            # TODO: Better Font Selection Strategy
            # For now, we look for 'SourceHanSansLite.ttf' in the game dir or commonly used paths
            # If not found, we can't calculate missing chars accurately without user input
            lite_font_path = None
            for root, _, files in os.walk(directory):
                if "SourceHanSansLite.ttf" in files:
                    lite_font_path = os.path.join(root, "SourceHanSansLite.ttf")
                    break
            
            missing_chars = set()
            if lite_font_path:
                scan_screen.set_status(f"Comparing with {os.path.basename(lite_font_path)}...")
                missing_chars = patcher.get_missing_characters(unique_chars, lite_font_path)
            else:
                # Fallback / Warning
                print("Warning: SourceHanSansLite.ttf not found. Skipping missing char calculation.")
                # We optionally could treat ALL as missing or NONE. 
                # For now let's assume 0 missing if we can't find the font, but flag it?
                pass
                
            scan_screen.set_progress(0.9)
            time.sleep(0.5)
            
            # 3. Complete
            scan_screen.set_status("Compiling results...")
            scan_screen.set_progress(1.0)
            time.sleep(0.5)
            
            # Populate Results
            results_screen = self.screens["results"]
            
            # Count rpy files for stats
            rpy_count = sum(1 for root, _, files in os.walk(directory) for f in files if f.endswith('.rpy'))
            
            results_screen.update_stats(
                files=rpy_count, 
                issues=len(missing_chars), 
                unique=len(unique_chars), 
                missing=len(missing_chars)
            )
            
            # Store data for next steps
            self.scan_data = {
                "directory": directory,
                "missing_chars": missing_chars,
                "unique_chars": unique_chars,
                "lite_font_path": lite_font_path
            }
            
            # Navigate
            self.navigate_to("results")
            
        except Exception as e:
            print(f"Scan Error: {e}")
            scan_screen.set_status(f"Error: {e}")
            # TODO: Show error UI

    def minimize(self, e):
        self.page.window_minimized = True
        self.page.update()

    def close(self, e):
        self.page.window_close()