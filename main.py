import flet as ft
from app.ui.app import RenPatchApp

def main(page: ft.Page):
    app = RenPatchApp(page)
    page.add(app)

if __name__ == "__main__":
    # app() is deprecated since 0.70, use run() instead
    # We check for run() availability for compatibility
    if hasattr(ft, 'run'):
        ft.run(target=main, assets_dir="assets")
    else:
        ft.app(target=main, assets_dir="assets")
