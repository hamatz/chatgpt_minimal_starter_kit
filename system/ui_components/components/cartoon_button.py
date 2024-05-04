import flet as ft

class CartoonButton(ft.UserControl):
    def __init__(self, text, on_click=None, **kwargs):
        super().__init__()
        self.text = text
        self.on_click = on_click if on_click else self.default_on_click
        self.color = kwargs.get("color", {"": ft.colors.LIGHT_BLUE_200, "hovered": ft.colors.LIGHT_BLUE_400})
        self.text_color = kwargs.get("text_color", {"": ft.colors.WHITE, "hovered": ft.colors.WHITE})
        self.icon = kwargs.get("icon", None)

    def default_on_click(self, _):
        print("Button clicked")

    def build(self):
        return ft.ElevatedButton(
            text=self.text,
            icon=self.icon,
            on_click=self.on_click,
            style=ft.ButtonStyle(
                bgcolor=self.color,
                color=self.text_color,
                shape=ft.RoundedRectangleBorder(radius=30),
                padding=ft.padding.all(10),
            ),
        )