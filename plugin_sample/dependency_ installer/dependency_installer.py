import base64
import os
import flet as ft
from api import API
from intent_conductor import IntentConductor
from interfaces.plugin_interface import PluginInterface

class DependencyInstaller(PluginInterface):
    _instance = None

    def __new__(cls, intent_conductor: IntentConductor, api):
        if cls._instance is None:
            cls._instance = super(DependencyInstaller, cls).__new__(cls)
            cls._instance.intent_conductor = intent_conductor
            cls._instance.api = api
        return cls._instance

    def load(self, page: ft.Page, function_to_top_page, plugin_dir_path: str):
        self.page = page
        self.page_back_func = function_to_top_page
        self.plugin_dir = plugin_dir_path

        page.clean()

        def go_back_to_home(e):
            self.page_back_func()

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
                
        icon_path = os.path.join(plugin_dir_path, "back_button.png")
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            app_icon = ft.Image(src_base64=encoded_string, width=30, height=30)
        clickable_icon = ft.GestureDetector(
            content=app_icon,
            on_tap=lambda _: go_back_to_home(None)
        )
        my_header_widget = get_component("SimpleHeader2", icon=clickable_icon, title_text="DependencyInstaller v.0.1.0", color="#20b2aa")
        page.add(my_header_widget)

        def install_dependencies(e):
            dependencies = [
                {"name": "plugin1", "url": "https://example.com/plugins/plugin1.zip"},
                {"name": "plugin2", "url": "https://example.com/plugins/plugin2.zip"},
                {"name": "plugin3", "url": "https://example.com/plugins/plugin3.zip"}
            ]
            try:
                self.api.logger.info(f"Installing dependencies: {dependencies}")
                self.intent_conductor.send_event("install_dependencies", {"dependencies": dependencies}, sender_plugin=self.__class__.__name__, target_plugin="PluginManagementProxy")
                self.page.snack_bar = ft.SnackBar(ft.Text("Dependencies installed successfully!"))
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as e:
                self.api.logger.error(f"Failed to install dependencies: {str(e)}")
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Failed to install dependencies: {str(e)}"))
                self.page.snack_bar.open = True
                self.page.update()

        install_button = get_component("CartoonButton", text="Install Dependencies", on_click=install_dependencies)

        self.page.add(
            ft.Container(
                content=ft.Text("Click the button to install dependencies:"),
                alignment=ft.alignment.center,
            ),
            ft.Container(
                content=install_button,
                alignment=ft.alignment.center,
            )
        )
        
        self.page.update()