import base64
import os
from urllib.parse import urlparse
import flet as ft
from interfaces.system_plugin_interface import SystemPluginInterface
from system_api_layer import SystemAPI
from intent_conductor import IntentConductor

class PluginManagementProxy(SystemPluginInterface):
    _instance = None

    def __new__(cls, system_api: SystemAPI, intent_conductor: IntentConductor, api):
        if cls._instance is None:
            cls._instance = super(PluginManagementProxy, cls).__new__(cls)
            cls._instance.system_api = system_api
            cls._instance.api = api
            cls._instance.intent_conductor = intent_conductor
            cls._instance.plugin_manager = None
            cls._instance.intent_conductor.register_plugin("PluginManagementProxy", cls._instance)
        return cls._instance

    def load(self, page: ft.Page, function_to_top_page, plugin_dir_path: str, loaded_callback):
        self.page = page
        self.page_back_func = function_to_top_page
        self.plugin_dir = plugin_dir_path

        loaded_callback()
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
        my_header_widget = get_component("SimpleHeader2", icon=clickable_icon, title_text="インストール用設定管理", color="#20b2aa")
        page.add(my_header_widget)

        def add_allowed_url(e):
            url = allowed_url_textbox.value
            if url:
                self.add_allowed_url(url)
                allowed_url_textbox.value = ""
                self.load_allowed_urls()
                page.update()

        allowed_url_textbox = get_component("CartoonTextBox", label="接続先情報", expand=True)
        add_button = get_component("CartoonButton", text="追加", on_click=add_allowed_url)

        allowed_urls_view = ft.ListView(expand=1, spacing=10, padding=20, auto_scroll=True)

        def load_allowed_urls():
            allowed_urls_view.controls.clear()
            allowed_urls = self.system_api.settings.load_system_dict("PluginManagementProxy", "allowed_urls")
            if allowed_urls:
                for url in allowed_urls.get("urls", []):
                    allowed_urls_view.controls.append(
                        ft.ListTile(
                            title=ft.Text(url),
                            bgcolor=ft.colors.GREY_200,
                            trailing=ft.IconButton(
                                icon=ft.icons.DELETE,
                                on_click=lambda _: self.remove_allowed_url(url),
                            ),
                        )
                    )

        self.load_allowed_urls = load_allowed_urls
        load_allowed_urls()

        page.add(
            ft.Container(
                content=ft.Text("接続を許可するサーバの情報を入力してください:", size=16),
                padding=20,
            ),
            ft.Container(
                content = ft.Row(
                    [
                        allowed_url_textbox,
                        add_button,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=20,
            ),
            allowed_urls_view,
        )

        page.update()

    def add_allowed_url(self, url):
        allowed_urls = self.system_api.settings.load_system_dict("PluginManagementProxy", "allowed_urls")
        if allowed_urls:
            if url not in allowed_urls.get("urls", []):
                allowed_urls["urls"].append(url)
        else:
            allowed_urls = {"urls": [url]}
        self.system_api.settings.save_system_dict("PluginManagementProxy", "allowed_urls", allowed_urls)

    def remove_allowed_url(self, url):
        allowed_urls = self.system_api.settings.load_system_dict("PluginManagementProxy", "allowed_urls")
        if allowed_urls and url in allowed_urls.get("urls", []):
            allowed_urls["urls"].remove(url)
            self.system_api.settings.save_system_dict("PluginManagementProxy", "allowed_urls", allowed_urls)
            self.load_allowed_urls()
            self.page.update()

    def is_allowed_url(self, url):
        allowed_urls = self.system_api.settings.load_system_dict("PluginManagementProxy", "allowed_urls")
        if allowed_urls:
            parsed_url = urlparse(url)
            for allowed_url in allowed_urls.get("urls", []):
                if allowed_url in parsed_url.netloc:
                    return True
        return False

    def show_error_dialog(self, message):
        def close_dialog(e):
            self.page.dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("エラー"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("閉じる", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()

    def install_dependencies(self, dependencies):
        for dependency in dependencies:
            plugin_name = dependency["name"]
            plugin_url = dependency["url"]
            if self.is_allowed_url(plugin_url):
                self.api.logger.info(f"Installing dependency: {plugin_name} from {plugin_url}")
                self.plugin_manager.install_plugin_from_url(plugin_url)
            else:
                error_message = f"依存プラグインのインストールが許可されていないURLです: {plugin_url}"
                self.api.logger.error(error_message)
                self.show_error_dialog(error_message)

    def set_plugin_manager(self, plugin_manager):
        self.plugin_manager = plugin_manager

    def handle_event(self, event_name, data, sender_plugin):
        if event_name == "set_plugin_manager" and sender_plugin == "PluginManager":
            self.plugin_manager = data
        elif event_name == "install_plugin" and self.plugin_manager:
            plugin_url = data.get("plugin_url")
            if self.is_allowed_url(plugin_url):
                self.api.logger.info(f"Installing plugin from: {plugin_url}")
                self.plugin_manager.install_plugin_from_url(plugin_url)
            else:
                error_message = f"プラグインのインストールが許可されていないURLです: {plugin_url}"
                self.api.logger.error(error_message)
                self.show_error_dialog(error_message)
        elif event_name == "install_dependencies" and self.plugin_manager:
            dependencies = data["dependencies"]
            self.install_dependencies(dependencies)