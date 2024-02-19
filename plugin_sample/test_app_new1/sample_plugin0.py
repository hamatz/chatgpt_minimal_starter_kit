import flet as ft
from plugin_interface import PluginInterface

class SamplePlugin(PluginInterface):
    # def __init__(self, ui_manager):
    #     self.ui_manager = ui_manager

    def load(self, page: ft.Page, function_to_top_page):
        my_header_cmp = self.ui_manager.get_component("simple_header")
        my_header_instance = my_header_cmp(ft.icons.TABLE_RESTAURANT, "Sample Plugin v.0.0.1", "#20b2aa", 5, 5)
        my_header_widget = my_header_instance.get_widget()
        greeting_text = ft.Text("はじめてのプラグインです", size=20)
        back_button = ft.ElevatedButton("Back to Main Page", on_click=lambda _: function_to_top_page())

        # 既存のUIをクリアして、新しいUIをページに追加
        page.clean()
        page.add(my_header_widget)
        page.add(greeting_text, back_button)
        page.update()
