import base64
import importlib
import json
import os
import flet as ft
from ui_component_manager import UIComponentManager
from system_api_layer import SystemAPI
from intent_conductor import IntentConductor
from interfaces.system_plugin_interface import SystemPluginInterface

class UIComponentToolkit(SystemPluginInterface):

    _instance = None

    def __new__(cls, system_api : SystemAPI, intent_conductor: IntentConductor):
        if cls._instance is None:
            cls._instance = super(UIComponentToolkit, cls).__new__(cls)
            cls._instance.system_api = system_api
            cls._instance.intent_conductor = intent_conductor
            cls._instance.component_dir = "system/ui_components/components"
            cls._instance.components = {}
            cls._instance.load_components()
            cls._instance.intent_conductor.register_plugin("UIComponentToolkit", cls._instance)
        return cls._instance

    def load_components(self):
        for filename in os.listdir(self.component_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = os.path.splitext(filename)[0]
                module_path = os.path.join(self.component_dir, filename)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for name in dir(module):
                    obj = getattr(module, name)
                    if isinstance(obj, type) and issubclass(obj, ft.UserControl):
                        self.components[name] = obj

    def get_component(self, component_name):
        return self.components.get(component_name)

    def handle_event(self, event_name, data, sender_plugin):
        #print(f"UIComponentToolkit handling event: {event_name}, Data: {data}, Sender: {sender_plugin}")
        if event_name == "get_component":
            component_name = data["component_name"]
            component_class = self.get_component(component_name)
            return component_class

    def send_event(self, event_name, data, target_plugin=None):
        self.intent_conductor.send_event(event_name, data, target_plugin)

    def load(self, page: ft.Page, function_to_top_page, plugin_dir_path: str, api):
        page.clean()

        icon_path = os.path.join(plugin_dir_path, "back_button.png")
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            app_icon = ft.Image(src_base64=encoded_string, width=30, height=30)
        clickable_icon = ft.GestureDetector(
            content=app_icon,
            on_tap=lambda _: function_to_top_page()
        )
        component_class = self.get_component("SimpleHeader2")
        my_header_widget = component_class(icon=clickable_icon, title_text="UI Component Catalog", color="#20b2aa")
        page.add(my_header_widget)

        def create_component_card(component_name, component_class):
            if component_name == "SimpleHeader":
                return ft.Container(
                    content=ft.Column([
                        ft.Text(component_name, size=18, weight="bold"),
                        component_class(icon=ft.icons.ADD_CARD, title_text=component_name, color="#20b2aa"),
                    ]),
                    alignment=ft.alignment.center,
                    bgcolor="#ffffff",
                    padding=10,
                    border_radius=10,
                )
            elif component_name == "SimpleHeader2":
                return ft.Container(
                    content=ft.Column([
                        ft.Text(component_name, size=18, weight="bold"),
                        component_class(icon=app_icon, title_text=component_name, color="#20b2aa"),
                    ]),
                    alignment=ft.alignment.center,
                    bgcolor="#ffffff",
                    padding=10,
                    border_radius=10,
                )
            elif component_name == "SimpleFooter":
                return ft.Container(
                    content=ft.Column([
                        ft.Text(component_name, size=18, weight="bold"),
                        component_class(title_text=component_name, color="#20b2aa"),
                    ]),
                    alignment=ft.alignment.center,
                    bgcolor="#ffffff",
                    padding=10,
                    border_radius=10,
                )
            elif component_name == "GlossyHeader":
                return ft.Container(
                    content=ft.Column([
                        ft.Text(component_name, size=18, weight="bold"),
                        component_class(title=component_name),
                    ]),
                    alignment=ft.alignment.center,
                    bgcolor="#ffffff",
                    padding=10,
                    border_radius=10,
                )                  
            else:
                return ft.Container(
                    content=ft.Column([
                        ft.Text(component_name, size=18, weight="bold"),
                        component_class(component_name),
                    ]),
                    alignment=ft.alignment.center,
                    bgcolor="#ffffff",
                    padding=10,
                    border_radius=10,
                )

        component_catalog = ft.GridView(
            expand=True,
            runs_count=5,
            max_extent=250,
            child_aspect_ratio=1.0,
            spacing=10,
            run_spacing=10,
        )

        for component_name, component_class in self.components.items():
            component_card = create_component_card(component_name, component_class)
            component_catalog.controls.append(component_card)

        page.add(component_catalog)