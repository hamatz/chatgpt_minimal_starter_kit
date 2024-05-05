import flet as ft

class CartoonSlider(ft.UserControl):
    def __init__(self, min_value, max_value, value=None, on_change=None, **kwargs):
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.on_change = on_change
        self.color = kwargs.get("color", ft.colors.BLUE_500)

    def build(self):
        return ft.Slider(
            min=self.min_value,
            max=self.max_value,
            value=self.value,
            on_change=self.on_change_handler,
            active_color=self.color,
        )

    def on_change_handler(self, e):
        self.value = e.control.value
        if self.on_change:
            self.on_change(e)