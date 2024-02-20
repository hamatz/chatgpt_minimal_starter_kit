import flet as ft
from system_plugin_interface import SystemPluginInterface

class SettingsPlugin(SystemPluginInterface):
    _instance = None
    
    def __new__(cls, ui_manager, system_api):
        if cls._instance is None:
            cls._instance = super(SettingsPlugin, cls).__new__(cls)
            cls._instance.ui_manager = ui_manager
            cls._instance.system_api = system_api
        return cls._instance

    def load(self, page: ft.Page, function_to_top_page, plugin_dir_path: str):
        my_header_cmp = self.ui_manager.get_component("simple_header")
        my_header_instance = my_header_cmp(ft.icons.SETTINGS, "Settings v.0.0.1", "#20b2aa")
        my_header_widget = my_header_instance.get_widget()
        greeting_text = ft.Text("システム設定", size=20)
        back_button = ft.ElevatedButton("Back to Main Page", on_click=lambda _: function_to_top_page())

        # 既存のUIをクリアして、新しいUIをページに追加
        page.clean()
        page.add(my_header_widget)
        page.add(greeting_text, back_button)
        page.update()
