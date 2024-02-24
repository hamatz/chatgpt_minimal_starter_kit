import flet as ft

class SimpleHeader2:
    def __init__(self, icon: ft.GestureDetector, title_text: str, color) -> ft.Container:
        self.header = ft.Container(
        content=ft.Row([
            icon,
            ft.Text(title_text, size=20),
        ], alignment="left"),
        bgcolor=color,
        padding=5,
        margin=0,
    )

    def get_widget(self):
        return self.header