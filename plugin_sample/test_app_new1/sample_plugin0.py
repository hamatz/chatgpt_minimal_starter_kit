import flet as ft
from interfaces.plugin_interface import PluginInterface

class SamplePlugin(PluginInterface):
    _instance = None
    
    def __new__(cls, ui_manager):
        if cls._instance is None:
            cls._instance = super(SamplePlugin, cls).__new__(cls)
            # 新しいインスタンスの初期化
            cls._instance.ui_manager = ui_manager
        return cls._instance

    def load(self, page: ft.Page, function_to_top_page, my_app_path: str):
        my_header_cmp = self.ui_manager.get_component("simple_header")
        my_header_instance = my_header_cmp(ft.icons.TABLE_RESTAURANT, "Sample Plugin v.0.0.1", "#20b2aa")
        my_header_widget = my_header_instance.get_widget()
        greeting_text = ft.Text("はじめてのプラグインです", size=20)
        back_button = ft.ElevatedButton("Back to Main Page", on_click=lambda _: function_to_top_page())

        # 既存のUIをクリアして、新しいUIをページに追加
        page.clean()
        page.add(my_header_widget)
        page.add(greeting_text, back_button)
        page.update()
