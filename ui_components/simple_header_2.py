import flet as ft

class SimpleHeader2:
    def __init__(self, icon: ft.GestureDetector, title_text: str, color) -> ft.Container:
        self.header = ft.Container(
        content=ft.Row([
            icon,
            ft.Text(title_text, size=20, color=ft.colors.WHITE),
        ], alignment="left"),
        bgcolor=color,
        padding=10,
        border_radius=ft.border_radius.all(10),
    )

    def get_widget(self):
        return self.header