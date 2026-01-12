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
from app.ui.screens.wizard import WizardScreen

class RenPatchApp(ft.Column):
    def __init__(self, page: ft.Page):
        super().__init__()
        # self.page = page # Removed to avoid AttributeError with ft.Control.page property
        self.expand = True
        self.spacing = 0
        self.alignment = ft.MainAxisAlignment.START
        
        # Configure Window - System Frame Enabled
        page.window_frameless = False # Enabled system title bar
        # page.window_bgcolor = "#00000000" # Not needed for system frame
        page.bgcolor = theme.colors.window_bg
        page.window_min_width = 800
        page.window_min_height = 600
        page.window_width = 1000
        page.window_height = 800
        page.title = "RedPanda RenPatch" # Set Window Title
        page.window_icon = "icons/favicon.png" # Attempt to set window/dock icon

        # Check for Administrator Privileges (Windows Only)
        try:
             import ctypes
             if os.name == 'nt' and ctypes.windll.shell32.IsUserAnAdmin():
                 print("WARNING: Running as Administrator on Windows. Drag-and-Drop will be blocked by UIPI.")
                 page.open(
                     ft.AlertDialog(
                         title=ft.Text("Warning: Running as Administrator"),
                         content=ft.Text(
                             "You are running RenPatch as an Administrator.\n\n"
                             "Windows security policies (UIPI) block dragging files from Explorer (running as user) "
                             "into an Admin application.\n\n"
                             "Please restart RenPatch as a normal user to use Drag-and-Drop, or use the 'Browse' button instead."
                         ),
                         actions=[ft.TextButton("I Understand", on_click=lambda e: page.close(page.dialog))]
                     )
                 )
        except Exception as e:
            print(f"Error checking admin status: {e}")
        
        # Initialize FilePicker
        self.file_picker = ft.FilePicker(on_result=self.on_directory_selected)
        page.overlay.append(self.file_picker)
        page.update()
        
        # Configure Global File Drop
        page.on_file_drop = self.on_file_drop
        
        # Initialize Screens
        self.screens = {
            "welcome": WelcomeScreen(on_start_click=lambda e: self.navigate_to("directory")),
            "directory": DirectoryScreen(
                on_browse_click=self.open_file_picker,
                on_directory_drop=lambda e: None, # Handled globally by page.on_file_drop
                on_start_scan_click=self.start_scanning,
                on_back_click=lambda e: self.navigate_to("welcome")
            ),
            "scanning": ScanningScreen(),
            "results": ResultsScreen(
                on_wizard_click=self.open_wizard,
                on_manual_click=lambda e: print("Manual clicked"),
                on_back_click=lambda e: self.navigate_to("directory")
            ),
            "wizard": WizardScreen(
                on_back_click=lambda e: self.navigate_to("results"),
                on_patch_complete_click=lambda e: print("Done")
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
                self._build_sidebar_item("⑤ Take Action", "wizard", disabled=True),
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

        # Updated controls
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
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH
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
            self._build_sidebar_item("③ Scan Project", "scanning", disabled=(screen_id not in ["scanning", "results", "wizard"])),
            self._build_sidebar_item("④ View Results", "results", disabled=(screen_id not in ["results", "wizard"])),
            self._build_sidebar_item("⑤ Take Action", "wizard", disabled=(screen_id != "wizard")),
        ]
        
        self.update()

    def open_file_picker(self, e):
        # FilePicker fixed by downgrading Flet to 0.28.2 (macOS regression in 0.28.3)
        try:
            self.file_picker.get_directory_path(
                initial_directory=os.path.expanduser("~/Downloads")
            )
        except Exception as ex:
            import traceback
            traceback.print_exc()
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error opening file picker: {ex}"))
            self.page.snack_bar.open = True
            self.page.update()

    def on_directory_selected(self, e: ft.FilePickerResultEvent):
        if e.path:
            # Update Directory Screen State
            self.screens["directory"].set_path(e.path)
            self.page.update()

    def on_file_drop(self, e):
        # NOTE: Drag-and-drop is currently deferred for future iteration.
        # Issues with Windows Admin privileges and macOS event firing.
        pass
        # if self.current_screen == "directory":
        #     if not e.files:
        #         return
        #     
        #     # Use the first dropped item's path string
        #     file_path = e.files[0].path
        #     
        #     # Check if it is a directory
        #     if os.path.isdir(file_path):
        #         # Update Directory Screen State via public method
        #         self.screens["directory"].set_path(file_path)
        #     else:
        #         # Show error feedback to user
        #         self.page.snack_bar = ft.SnackBar(ft.Text("Please drop a directory, not a file."))
        #         self.page.snack_bar.open = True
        #         self.page.update()

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
            time.sleep(0.5) 
            
            unique_chars = scanner.get_unique_characters(directory)
            scan_screen.set_status(f"Found {len(unique_chars)} unique characters...")
            scan_screen.set_progress(0.3)
            
            # 2. Heuristic Font Analysis
            scan_screen.set_status("Locating project fonts...")
            font_files = scanner.find_fonts(directory)
            
            # Prepare data
            font_health_data = []
            
            total_fonts = len(font_files)
            processed_fonts = 0
            
            if not font_files:
                scan_screen.set_status("No fonts found in project.")
                time.sleep(1)
            else:
                for font_path in font_files:
                    filename = os.path.basename(font_path)
                    scan_screen.set_status(f"Analyzing {filename}...")
                    
                    # Determine Role
                    role, confidence = scanner.analyze_font_role(directory, font_path)
                    
                    # Calculate Health
                    missing_chars = patcher.get_missing_characters(unique_chars, font_path)
                    
                    font_health_data.append({
                        "file_path": font_path,
                        "role": role,
                        "confidence": confidence,
                        "missing_count": len(missing_chars),
                        "total_chars": len(unique_chars),
                        "missing_set": missing_chars # Store for later patching
                    })
                    
                    processed_fonts += 1
                    scan_screen.set_progress(0.3 + (0.6 * (processed_fonts / total_fonts)))

            # Sort data: Dialogue > UI > Unknown
            role_priority = {"Dialogue": 0, "Name/UI": 1, "UI": 2, "Unknown": 3}
            font_health_data.sort(key=lambda x: role_priority.get(x["role"], 99))

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
            
            global_stats = {
                "files": rpy_count,
                "unique_chars": len(unique_chars)
            }
            
            results_screen.update_data(global_stats, font_health_data)
            
            # Store data for wizard usage
            self.scan_data = {
                "directory": directory,
                "unique_chars": unique_chars,
                "fonts": font_health_data
            }
            
            # Navigate
            self.navigate_to("results")
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Scan Error: {e}")
            scan_screen.set_status(f"Error: {e}")

    def open_wizard(self, font_data):
        self.screens["wizard"].set_data(font_data, self.scan_data)
        self.navigate_to("wizard")

    def minimize(self, e):
        self.page.window_minimized = True
        self.page.update()

    def close(self, e):
        self.page.window_close()