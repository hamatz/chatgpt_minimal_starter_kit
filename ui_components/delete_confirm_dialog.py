import flet as ft

class DeleteConfirmDialog(ft.UserControl):
    def __init__(self, title_text: str, content_text: str, text_no: str, text_yes: str, func_close_dlg, function_on_click, delete_target):
        super().__init__()
        self.title_text = title_text
        self.content_text = content_text
        self.text_no = text_no
        self.text_yes = text_yes
        self.func_close_dlg = func_close_dlg
        self.function_on_click = function_on_click
        self.delete_target = delete_target

    def build(self):
        return ft.AlertDialog(
            modal=True,
            title=ft.Text(self.title_text, size=20, color=ft.colors.BLACK, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Text(self.content_text, size=16, color=ft.colors.BLACK),
                padding=20,
                bgcolor=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=[ft.colors.CYAN_50, ft.colors.BLUE_50],
                ),
                #border=ft.border.all(2, ft.colors.BLACK),
                border_radius=ft.border_radius.all(10),
            ),
            actions=[
                ft.TextButton(self.text_no, on_click=lambda e: self.func_close_dlg(e)),
                ft.TextButton(self.text_yes, on_click=lambda e: self.function_on_click(self.delete_target)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )