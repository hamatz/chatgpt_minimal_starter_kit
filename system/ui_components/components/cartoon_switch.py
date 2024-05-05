import flet as ft

class CartoonSwitch(ft.UserControl):
    def __init__(self, label, value=False, on_change=None, **kwargs):
        super().__init__()
        self.label = label
        self.value = value
        self.on_change = on_change
        self.color = kwargs.get("color", ft.colors.BLUE_500)
        self.disabled= kwargs.get("disabled", False)

    def build(self):
        return ft.Row(
            controls=[
                ft.Switch(value=self.value, on_change=self.on_change_handler, active_color=self.color, disabled=self.disabled),
                ft.Text(self.label),
            ],
        )

    def on_change_handler(self, e):
        self.value = e.control.value
        if self.on_change:
            self.on_change(e)