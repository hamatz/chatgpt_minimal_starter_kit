import flet as ft

class AppContainer:
    def __init__(self, title_text: str, image: ft.GestureDetector, color) -> ft.Container:
        self.container = ft.Container(
        content=ft.Column([
            image,
            ft.Text(title_text, size=10),
        ], horizontal_alignment= ft.CrossAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        bgcolor=color,
        padding=2,
        margin=3,
    )

    def get_widget(self):
        return self.container