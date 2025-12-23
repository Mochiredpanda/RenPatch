import flet as ft

def main(page: ft.Page):
    page.title = "RenPatch (RPRP)"
    page.window.width = 900
    page.window.height = 700
    page.padding = 0
    # 2010s Theme Background
    page.bgcolor = "#ecf0f1"
    
    # TODO: Load custom theme and initialize different screens
    
    t = ft.Text(value="RenPatch GUI Initialized", color="black", size=30)
    page.add(ft.Container(content=t, alignment=ft.alignment.center, expand=True))

if __name__ == "__main__":
    ft.app(target=main)
