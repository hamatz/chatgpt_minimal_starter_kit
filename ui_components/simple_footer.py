import flet as ft

class SimpleFooter:
    def __init__(self, title_text: str, color) -> ft.Container:
        self.footer = ft.Container(
        content=ft.Row([
            ft.Text(title_text, size=10),
        ], alignment="center"),
        bgcolor=color,
        padding=5,
        margin=0,
    )

    def get_widget(self):
        return self.footer