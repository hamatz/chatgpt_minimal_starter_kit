import flet as ft

class SimpleHeader:
    def __init__(self, icon: ft.Icon, title_text: str, color) -> ft.Container:
        self.header = ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=20, color=ft.colors.WHITE),
                ft.Text(title_text, size=20, color=ft.colors.WHITE),
            ], alignment=ft.MainAxisAlignment.START),
            bgcolor=color,
            padding=10,
            border_radius=ft.border_radius.all(10),
        )

    def get_widget(self):
        return self.header