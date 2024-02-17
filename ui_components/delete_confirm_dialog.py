import flet as ft

class DeleteConfirmDialog:
    def __init__(self, title_text: str, content_text: str, text_no: str, text_yes: str, func_close_dlg, function_on_click, delete_target: list):
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title_text),
            content=ft.Text(content_text),
            actions=[
                ft.TextButton(text_no, on_click=lambda e: func_close_dlg(e)),
                ft.TextButton(text_yes, on_click=lambda e: function_on_click(delete_target))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def get_widget(self):
        return self.dialog