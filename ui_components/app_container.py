import flet as ft

class AppContainer:
    def __init__(self, title_text: str, image: ft.GestureDetector, color, padding: int, margin: int) -> ft.Container:
        self.container = ft.Container(
        content=ft.Column([
            image,
            ft.Text(title_text, size=10),
        ], alignment="center"),
        bgcolor=color,
        padding=padding,
        margin=margin,
    )

    def get_widget(self):
        return self.container