import flet as ft

class SimpleFooter(ft.UserControl):
    def __init__(self, **kwargs):
        super().__init__()
        self.title_text = kwargs.get("title_text")
        self.color = kwargs.get("color")

    def build(self):
        return ft.Container(
            content=ft.Row([
                ft.Text(self.title_text, size=12, color=ft.colors.WHITE),
            ], alignment="center"),
            bgcolor=self.color,
            padding=10,
            border_radius=ft.border_radius.all(10),
        )