import flet as ft

class SimpleHeader(ft.UserControl):
    def __init__(self, **kwargs):
        super().__init__()
        self.icon = kwargs.get("icon")
        self.title_text = kwargs.get("title_text")
        self.color = kwargs.get("color")

    def build(self):
        return ft.Container(
            content=ft.Row([
                ft.Icon(self.icon, size=20, color=ft.colors.WHITE),
                ft.Text(self.title_text, size=20, color=ft.colors.WHITE),
            ], alignment=ft.MainAxisAlignment.START),
            bgcolor=self.color,
            padding=10,
            border_radius=ft.border_radius.all(10),
        )