import flet as ft

class SimpleFooter:
    def __init__(self, title_text: str, color) -> ft.Container:
        self.footer = ft.Container(
            content=ft.Row([
                ft.Text(title_text, size=12, color=ft.colors.WHITE),
            ], alignment="center"),
            bgcolor=color,
            padding=10,
            border_radius=ft.border_radius.all(10),
        )

    def get_widget(self):
        return self.footer