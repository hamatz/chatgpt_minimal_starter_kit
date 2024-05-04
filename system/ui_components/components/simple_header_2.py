import flet as ft

class SimpleHeader2(ft.UserControl):
    def __init__(self, **kwargs):
        super().__init__()
        self.icon = kwargs.get("icon")
        self.title_text = kwargs.get("title_text")
        self.color = kwargs.get("color")

    def build(self):
        icon = self.icon
        if isinstance(icon, dict):
            content = ft.Image(src_base64=icon["content"]) if icon["content"] else None
            on_tap = eval(icon["on_tap"]) if icon["on_tap"] else None
            icon = ft.GestureDetector(content=content, on_tap=on_tap)
        title_text = self.title_text
        color = self.color
        return ft.Container(
            content=ft.Row([
                icon,
                ft.Text(title_text, size=20, color=ft.colors.WHITE),
            ], alignment="left"),
            bgcolor=color,
            padding=10,
            border=ft.border.all(1, ft.colors.BLACK),
            border_radius=ft.border_radius.all(30),
            ink=True,  # ドロップシャドウ効果を追加
        )