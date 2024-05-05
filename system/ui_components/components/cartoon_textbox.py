import flet as ft

class CartoonTextBox(ft.UserControl):
    def __init__(self, label, **kwargs):
        super().__init__()
        self.label = label
        self.border_color = kwargs.get("border_color", ft.colors.BLACK)
        self.text_color = kwargs.get("text_color", ft.colors.BLACK)
        self.bgcolor = kwargs.get("bgcolor", ft.colors.WHITE)

    def build(self):
        return ft.TextField(
            label=self.label,
            border_color=self.border_color,
            text_style=ft.TextStyle(color=self.text_color),
            border_radius=ft.border_radius.all(30),
            filled=True,
            expand=True,
            bgcolor=self.bgcolor,
        )