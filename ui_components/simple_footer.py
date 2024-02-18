import flet as ft

class SimpleFooter:
    def __init__(self, title_text: str, color, padding: int, margin: int) -> ft.Container:
        self.footer = ft.Container(
        content=ft.Row([
            ft.Text(title_text, size=10),
        ], alignment="center"),
        bgcolor=color,
        padding=padding,
        margin=margin,
    )

    def get_widget(self):
        return self.footer