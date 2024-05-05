import flet as ft

class CartoonDropdown(ft.UserControl):
    def __init__(self, options, value=None, on_change=None, **kwargs):
        super().__init__()
        self.options = options
        self.value = value
        self.on_change = on_change
        self.txt_color = kwargs.get("txt_color", ft.colors.BLUE_500)
        self.bg_color = kwargs.get("bg_color", ft.colors.WHITE)

    def build(self):
        return ft.Dropdown(
            options=[
                ft.dropdown.Option(option)
                for option in self.options
            ],
            value=self.value,
            on_change=self.on_change_handler,
            color=self.txt_color,
            bgcolor=self.bg_color,
            alignment=ft.alignment.center ,
            border_color=ft.colors.BLACK,
            filled=True,
            border_radius=30,
        )

    def on_change_handler(self, e):
        self.value = e.control.value
        if self.on_change:
            self.on_change(e)