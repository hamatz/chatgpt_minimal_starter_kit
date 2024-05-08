import flet as ft

class CartoonTextBox(ft.UserControl):
    def __init__(self, label, value=None, on_change=None, on_focus=None, **kwargs):
        super().__init__()
        self.label = label
        self.value = value
        self.user_on_change = on_change
        self.user_on_focus = on_focus
        self.border_color = kwargs.get("border_color", ft.colors.BLACK)
        self.text_color = kwargs.get("text_color", ft.colors.BLACK)
        self.bgcolor = kwargs.get("bgcolor", ft.colors.WHITE)
        self.expand = kwargs.get("expand", False)

    def build(self):
        self.text_field = ft.TextField(
            label=self.label,
            border_color=self.border_color,
            text_style=ft.TextStyle(color=self.text_color),
            border_radius=ft.border_radius.all(30),
            filled=True,
            expand=self.expand,
            bgcolor=self.bgcolor,
            value=self.value,
            on_change=self.on_change,
            on_focus=self.on_focus,
        )
        return self.text_field

    def on_change(self, e):
        self.value = e.control.value
        if self.user_on_change:
            self.user_on_change(e)

    def on_focus(self, e):
        self.value = e.control.value
        if self.user_on_focus:
            self.user_on_focus(e)

    def set_value(self, value):
        self.text_field.value = value
        self.text_field.update()

    def get_value(self):
        return self.text_field.value