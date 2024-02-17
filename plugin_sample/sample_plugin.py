import flet as ft

def build_ui(page: ft.Page, function_to_previous_page):
    greeting_text = ft.Text("Welcome to the Plugin Page!", size=20)
    back_button = ft.ElevatedButton("Back to Main Page", on_click=lambda _: function_to_previous_page())

    # 既存のUIをクリアして、新しいUIをページに追加
    page.clean()
    page.add(greeting_text, back_button)
    page.update()