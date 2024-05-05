import flet as ft
from interfaces.plugin_interface import PluginInterface

class SamplePlugin(PluginInterface):
    _instance = None
    
    def __new__(cls, intent_conductor, api):
        if cls._instance is None:
            cls._instance = super(SamplePlugin, cls).__new__(cls)
            # 新しいインスタンスの初期化
            cls._instance.intent_conductor = intent_conductor
            cls._instance.api = api
        return cls._instance

    def load(self, page: ft.Page, function_to_top_page, my_app_path: str):

        def get_component(component_name, **kwargs):
            self.api.logger.info(f"Requesting component: {component_name}")
            target_component = {"component_name": component_name}
            response = self.intent_conductor.send_event("get_component", target_component, sender_plugin=self.__class__.__name__, target_plugin="UIComponentToolkit")
            if response:
                component_class = response
                self.api.logger.info(f"Received component: {component_name}")
                return component_class(**kwargs)
            else:
                self.api.logger.error(f"component cannot be found: {component_name}")

        my_header_widget = get_component("SimpleHeader", icon=ft.icons.TABLE_RESTAURANT, title_text="Sample Plugin v.0.1.0", color="#20b2aa")

        greeting_text = ft.Text("はじめてのプラグインです", size=20)
        back_button = ft.ElevatedButton("Back to Main Page", on_click=lambda _: function_to_top_page())

        page.clean()
        page.add(my_header_widget)
        page.add(greeting_text, back_button)
        page.update()