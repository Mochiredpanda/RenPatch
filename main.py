import flet as ft
from app.ui.app import RenPatchApp

def main(page: ft.Page):
    app = RenPatchApp(page)
    page.add(app)

if __name__ == "__main__":
    # ft.app is the standard entry point for Flet applications
    ft.app(target=main, assets_dir="assets")
