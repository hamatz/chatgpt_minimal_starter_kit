import flet as ft

class SimpleHeader:
    def __init__(self, icon: ft.Icon, title_text: str, color, padding: int, margin: int) -> ft.Container:
        self.header = ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=20),
            ft.Text(title_text, size=20),
        ], alignment="left"),
        bgcolor=color,
        padding=padding,
        margin=margin
    )

    def get_widget(self):
        return self.header