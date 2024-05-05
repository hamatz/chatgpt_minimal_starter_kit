import flet as ft

class CartoonRadioGroup(ft.UserControl):
    def __init__(self, options, value=None, on_change=None, **kwargs):
        super().__init__()
        self.options = options
        self.value = value
        self.on_change = on_change
        self.color = kwargs.get("color", ft.colors.BLUE_500)

    def build(self):
        return ft.RadioGroup(content=ft.Column(
            controls=[
                ft.Radio(
                    value=option,
                    label=option,
                    fill_color=self.color
                )
                for option in self.options
            ],), on_change=self.on_change)
        