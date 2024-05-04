import flet as ft

class AppContainer(ft.UserControl):
    def __init__(self, title_text: str, version_text: str, image: ft.GestureDetector, color):
        super().__init__()
        self.title_text = title_text
        self.version_text = version_text
        self.image = image
        self.color = color

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=self.image,
                    padding=1,
                    border=ft.border.all(1, self.color),
                    border_radius=ft.border_radius.all(5),
                ),
                ft.Text(self.title_text, size=10),
                ft.Text(self.version_text, size=8),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.center,
            padding=2,
            margin=3,
        )