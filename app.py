import flet as ft
from plugin_manager import PluginManager
from my_key_manager import MyKeyManager
from ui_component_manager import UIComponentManager
from ui_components.password_dialog import PasswordDialog
from ui_components.delete_confirm_dialog import DeleteConfirmDialog
from ui_components.simple_header import SimpleHeader

class CraftForgeBase:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.page.title = "ChatGPT minimal starter kit"
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.ui_manager = UIComponentManager()
        self.ui_manager.add_component("password_daialog", PasswordDialog)
        self.ui_manager.add_component("delete_confirm_daialog", DeleteConfirmDialog)
        self.ui_manager.add_component("simple_header", SimpleHeader)
        self.mkm = MyKeyManager(self.page, self.ui_manager)
        self.pm = PluginManager(self.page, self.page_back, self.ui_manager)
        self.mkm.load_my_key()

    def show_main_page(self) -> None:
        def pick_file_and_install(e: ft.FilePickerResultEvent):
            self.pm.install_plugin(e)

        my_header_cmp = self.ui_manager.get_component("simple_header")
        my_header_instance = my_header_cmp(ft.icons.MENU_ROUNDED, "CraftForge v.0.0.1", "#20b2aa", 5, 5)
        my_header_widget = my_header_instance.get_widget()
        self.page.add(my_header_widget)
        self.pm.load_installed_plugins()
        # プラグインをインストールするボタンを表示する
        file_picker = ft.FilePicker(on_result=pick_file_and_install)
        self.page.overlay.append(file_picker)
        install_button = ft.ElevatedButton("Install Plugin", icon=ft.icons.UPLOAD_FILE, on_click=lambda _:file_picker.pick_files())
        self.page.add(install_button)
        self.page.update()

    def page_back(self) -> None:
        self.page.clean()
        self.show_main_page()

def main(page: ft.Page) -> None:
    app = CraftForgeBase(page)
    app.show_main_page()

if __name__ == "__main__":
    ft.app(target=main)

