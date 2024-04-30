import flet as ft

class AppContainer:
    def __init__(self, title_text: str, version_text: str, image: ft.GestureDetector, color) -> ft.Container:
        self.container = ft.Container(
        content=ft.Column([
            ft.Container(
                content=image,
                padding=1,
                border=ft.border.all(1, color),
                border_radius=ft.border_radius.all(5),
            ),
            ft.Text(title_text, size=10),
            ft.Text(version_text, size=8),
        ], horizontal_alignment= ft.CrossAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        padding=2,
        margin=3,
    )

    def get_widget(self):
        return self.container