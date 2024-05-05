import flet as ft

class CartoonProgressBar(ft.UserControl):
    def __init__(self, value, **kwargs):
        super().__init__()
        self.value = value
        self.color = kwargs.get("color", ft.colors.BLUE_500)
        self.height = kwargs.get("bar_height", 8)

    def build(self):
        return ft.ProgressBar(
            value=self.value,
            color=self.color,
            bgcolor=ft.colors.GREY_300,
            bar_height=self.height,
            #border_radius=ft.border_radius.all(30),
        )