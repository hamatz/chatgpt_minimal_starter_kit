import flet as ft

class GlossyHeader(ft.UserControl):
    def __init__(self, **kwargs):
        super().__init__()
        self.title = kwargs.get("title")

    def build(self):
        return ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        self.title,
                        size=20,
                        color=ft.colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    )         
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.all(15),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.colors.LIGHT_BLUE_400, ft.colors.LIGHT_BLUE_700],
            ),
            border=ft.border.only(
                left=ft.border.BorderSide(width=2, color=ft.colors.WHITE54),
                top=ft.border.BorderSide(width=2, color=ft.colors.WHITE),
                right=ft.border.BorderSide(width=2, color=ft.colors.WHITE),
                bottom=ft.border.BorderSide(width=2, color=ft.colors.WHITE54),
            ),
        )