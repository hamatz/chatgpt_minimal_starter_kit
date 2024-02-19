import flet as ft

class PasswordDialog:
    def __init__(self, title_text: str, label_text: str, function_on_change, text_complete: str, function_on_click):
        self.dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title_text, size=16),
            content= ft.TextField(
                label=label_text, 
                password=True, 
                on_change=lambda e:function_on_change(e),),
            actions=[
                ft.TextButton(text_complete, on_click=lambda e: function_on_click(e)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def get_widget(self):
        return self.dialog