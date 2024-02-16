import flet as ft
from plugin_manager import PluginManager

def show_main_page(page: ft.Page):
    def pick_file_and_install(e: ft.FilePickerResultEvent):
        pm.install_plugin(e)

    page.title = "ChatGPT minimal starter kit"
    page.vertical_alignment = ft.MainAxisAlignment.START
    pm = PluginManager(page, page_back)
    # インストール済みのプラグインを読み込む
    pm.load_installed_plugins()
    # プラグインをインストールするボタンを表示する
    file_picker = ft.FilePicker(on_result=pick_file_and_install)
    page.overlay.append(file_picker)
    install_button = ft.ElevatedButton("Install Plugin", icon=ft.icons.UPLOAD_FILE, on_click=lambda _:file_picker.pick_files())
    page.add(install_button)
    page.update()

def page_back(page: ft.Page):
    page.clean()
    show_main_page(page)

def main(page: ft.Page):
    show_main_page(page)

if __name__ == "__main__":
    ft.app(target=main)

