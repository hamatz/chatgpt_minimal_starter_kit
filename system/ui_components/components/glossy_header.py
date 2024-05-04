import flet as ft

class GlossyHeader(ft.UserControl):
    def __init__(self, **kwargs):
        super().__init__()
        self.title = kwargs.get("title")
        self.color_1 = kwargs.get("color_1", ft.colors.LIGHT_BLUE_400)
        self.color_2 = kwargs.get("color_2", ft.colors.LIGHT_BLUE_700)

    def build(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        self.title,
                        size=18,
                        color=ft.colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    )         
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(10),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[self.color_1, self.color_2],
            ),
            border=ft.border.all(1, ft.colors.BLACK),
            border_radius=ft.border_radius.all(30),
        )