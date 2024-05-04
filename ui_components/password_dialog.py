import flet as ft

class PasswordDialog(ft.UserControl):
    def __init__(self, title_text: str, label_text: str, function_on_change, text_complete: str, function_on_click):
        super().__init__()
        self.title_text = title_text
        self.label_text = label_text
        self.function_on_change = function_on_change
        self.text_complete = text_complete
        self.function_on_click = function_on_click

    def build(self):
        return ft.AlertDialog(
            modal=True,
            title=ft.Text(self.title_text, size=20, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.TextField(
                    label=self.label_text,
                    password=True,
                    on_change=lambda e: self.function_on_change(e),
                    border_color=ft.colors.BLUE_GREY_400,
                    focused_border_color=ft.colors.BLUE_700,
                    border_radius=ft.border_radius.all(8),
                ),
                padding=20,
                bgcolor=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[ft.colors.PINK_50, ft.colors.PURPLE_50],
                ),
                #border=ft.border.all(2, ft.colors.BLACK),
                border_radius=ft.border_radius.all(10),
            ),
            actions=[
                ft.TextButton(self.text_complete, on_click=lambda e: self.function_on_click(e)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )