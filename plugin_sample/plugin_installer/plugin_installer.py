import base64
import os
import flet as ft
from api import API
from intent_conductor import IntentConductor
from interfaces.plugin_interface import PluginInterface

class PluginInstaller(PluginInterface):
    _instance = None

    def __new__(cls, intent_conductor: IntentConductor):
        if cls._instance is None:
            cls._instance = super(PluginInstaller, cls).__new__(cls)
            cls._instance.intent_conductor = intent_conductor
        return cls._instance

    def load(self, page: ft.Page, function_to_top_page, plugin_dir_path: str, api):
        self.page = page
        self.page_back_func = function_to_top_page
        self.plugin_dir = plugin_dir_path
        self.api = api

        page.clean()

        def go_back_to_home(e):
            self.page_back_func()

        def get_component(component_name, **kwargs):
            api.logger.info(f"Requesting component: {component_name}")
            target_component = {"component_name": component_name}
            response = self.intent_conductor.send_event("get_component", target_component, sender_plugin=self.__class__.__name__, target_plugin="UIComponentToolkit")
            if response:
                component_class = response
                api.logger.info(f"Received component: {component_name}")
                return component_class(**kwargs)
            else:
                api.logger.error(f"component cannot be found: {component_name}")

        icon_path = os.path.join(plugin_dir_path, "back_button.png")
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            app_icon = ft.Image(src_base64=encoded_string, width=30, height=30)
        clickable_icon = ft.GestureDetector(
            content=app_icon,
            on_tap=lambda _: go_back_to_home(None)
        )
        my_header_widget = get_component("SimpleHeader2", icon=clickable_icon, title_text="PluginInstaller v.0.1.0", color="#20b2aa")
        page.add(my_header_widget)

        def install_plugin(e):
            plugin_url = plugin_url_textbox.value
            if plugin_url:
                try:
                    self.api.logger.info(f"Installing plugin from: {plugin_url}")
                    # Request plugin installation via PluginManagementProxy
                    self.intent_conductor.send_event("install_plugin", {"plugin_url": plugin_url}, sender_plugin=self.__class__.__name__, target_plugin="PluginManagementProxy")
                    self.page.snack_bar = ft.SnackBar(ft.Text(f"Plugin '{plugin_url}' installed successfully!"))
                    self.page.snack_bar.open = True
                    plugin_url_textbox.value = ""
                    self.page.update()
                except Exception as e:
                    self.api.logger.error(f"Failed to install plugin: {str(e)}")
                    self.page.snack_bar = ft.SnackBar(ft.Text(f"Failed to install plugin: {str(e)}"))
                    self.page.snack_bar.open = True
                    self.page.update()

        plugin_url_textbox = get_component("CartoonTextBox", label="Plugin URL")
        install_button = get_component("CartoonButton", text="Install",  on_click=install_plugin)

        self.page.add(
            ft.Container(
                content=ft.Text("Enter the plugin url to install:"),
                alignment=ft.alignment.center_left,
            ),
            ft.Container(
                content=ft.Column(
                    [                       
                        plugin_url_textbox,
                        install_button,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                ),
            )
        )
        
        self.page.update()