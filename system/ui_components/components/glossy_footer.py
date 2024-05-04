import flet as ft

class GlossyFooter(ft.UserControl):
    def __init__(self, **kwargs):
        super().__init__()
        self.title_text = kwargs.get("title_text")
        self.color_1 = kwargs.get("color_1", ft.colors.LIGHT_BLUE_400)
        self.color_2 = kwargs.get("color_2", ft.colors.LIGHT_BLUE_700)

    def build(self):
        return ft.Container(
            content=ft.Row([
                ft.Text(self.title_text, size=12, color=ft.colors.WHITE),
            ], alignment="center"),
            padding=10,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[self.color_1, self.color_2],
            ),
            border=ft.border.all(1, ft.colors.BLACK),
            border_radius=ft.border_radius.all(30),
        )