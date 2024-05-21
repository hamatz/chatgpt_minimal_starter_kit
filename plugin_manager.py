import base64
import tempfile
import uuid
import zipfile
import os
import sys
import shutil
import json
import importlib
import flet as ft
from typing import Callable, Dict

import requests
from interfaces.plugin_interface import PluginInterface
from interfaces.system_plugin_interface import SystemPluginInterface
from intent_conductor import IntentConductor
from system_api_layer import SystemAPI
from api import API
from code_security_scanner import CodeSecurityScanner
from ui_components.delete_confirm_dialog import DeleteConfirmDialog
from ui_components.app_container import AppContainer

PLUGIN_FOLDER = "installed_plugins"
SYSTEM_PLUGIN_FOLDER = "system"

class PluginManager:

    def __init__(self, page: ft.Page, page_back : Callable[[], None], system_api: SystemAPI, base_dir: str, save_dir: str, api : API, intent_conductor: IntentConductor):
        self.page = page
        self.page_back_func = page_back
        self.plugin_dict = {}
        self.__system_api = system_api
        self.api = api
        self.intent_conductor = intent_conductor
        self.plugin_folder_path = os.path.join(save_dir, PLUGIN_FOLDER)
        self.system_plugin_folder_path = os.path.join(base_dir, SYSTEM_PLUGIN_FOLDER)
        self.myapp_container = None
        self.installed_plugins: Dict[str, str] = {} 
        self.load_installed_plugins_info()
        
        if not os.path.exists(self.plugin_folder_path):
            os.makedirs(self.plugin_folder_path)
        if not os.path.exists(self.system_plugin_folder_path):
            os.makedirs(self.system_plugin_folder_path)

    def load_installed_plugins_info(self):
        target_list = [filename for filename in os.listdir(self.plugin_folder_path) if not filename.startswith('.')]
        for plugin_name in target_list:
            plugin_dir = os.path.join(self.plugin_folder_path, plugin_name)
            if os.path.isdir(plugin_dir):
                with open(os.path.join(plugin_dir, "plugin.json"), 'r', encoding='utf-8') as f:
                    plugin_info = json.load(f)
                self.installed_plugins[plugin_info["plugin_name"]] = plugin_dir

    def _load_plugin(self, plugin_dir: str, container: ft.Container):
        try:
            with open(os.path.join(plugin_dir, "plugin.json"), 'r', encoding='utf-8') as f:
                plugin_info = json.load(f)
        except UnicodeDecodeError as e:
            self.api.logger.error(f"Error decoding plugin.json: {e}")
            return  # エラー時は処理を中断
        
        use_camera = plugin_info.get("use_camera", False)
        use_microphone = plugin_info.get("use_microphone", False)
        plugin_name = plugin_info.get("plugin_name")
        
        # 既存のパーミッション情報を取得
        existing_permissions = self.__system_api.settings.load_system_dict("PluginPermissions", plugin_name)
        if existing_permissions is None:
            existing_permissions = {}
        
        # 既存のパーミッション情報があれば、それを残す
        camera_allowed = existing_permissions.get("camera_allowed", False)
        microphone_allowed = existing_permissions.get("microphone_allowed", False)
        
        # パーミッション情報を保存
        self.__system_api.settings.save_system_dict("PluginPermissions", plugin_name, {
            "use_camera": use_camera,
            "use_microphone": use_microphone,
            "camera_allowed": camera_allowed,
            "microphone_allowed": microphone_allowed,
        })
        sys.path.append(plugin_dir)
        plugin_module = importlib.import_module(plugin_info["main_module"])
        plugin_class = getattr(plugin_module, plugin_info["plugin_name"])
        # システムプラグインかどうかに基づき、インスタンスを作成
        if "system" in plugin_dir:
            plugin_instance = plugin_class(self.__system_api, self.intent_conductor, self.api)
        else:
            plugin_instance = plugin_class(self.intent_conductor, self.api)
        # アイコン画像の読み込みとエンコード
        try:
            icon_path = os.path.join(plugin_dir, plugin_info["icon"])
            with open(icon_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            self.api.logger.error(f"Error loading or encoding icon: {e}")
            encoded_string = ""  # エラー時はエンコード済み文字列を空に

        app_icon = ft.Image(src_base64=encoded_string, width=100, height=100)
        clickable_image = ft.GestureDetector(
            content=app_icon,
            on_tap=lambda _: show_plugin(plugin_instance, plugin_dir, app_container_instance)
        )
        app_title = plugin_info["name"]
        app_version = "Version: " + plugin_info["version"]
        app_container_instance = AppContainer(app_title, app_version, clickable_image, "#ffffff" if "system" not in plugin_dir else "#20b2aa")

        if "system" in plugin_dir:
            container.controls.append(app_container_instance)
        else:
            plugin_name = plugin_info["plugin_name"]
            
            if plugin_name in self.plugin_dict:
                self.plugin_dict[plugin_name].content = app_container_instance
            else:
                deletable_app_container = ft.GestureDetector(
                    content=app_container_instance,
                    on_long_press_start=lambda e: self.show_delete_confirmation(plugin_dir, plugin_name)
                )
                container.controls.append(deletable_app_container)
                self.plugin_dict[plugin_name] = deletable_app_container
            
            self.myapp_container = container
            self.installed_plugins[plugin_name] = plugin_dir

        def show_plugin(instance, plugin_dir, app_container_instance):
            spinner = ft.ProgressRing(color=ft.colors.TEAL_ACCENT_400, stroke_width=8, scale=0.8)
            spinner_overlay = ft.Container(
                content=spinner,
                alignment=ft.alignment.center,
                width=100,
                height=100,
                bgcolor=ft.colors.BLACK54,
                border_radius=ft.border_radius.all(10),
            )
            plugin_icon_stack = ft.Stack(
                [
                    app_container_instance.image.content,
                    spinner_overlay,
                ],
                width=100,
                height=100,
            )
            app_container_instance.image.content = plugin_icon_stack
            app_container_instance.image.update()

            self.page.overlay.append(app_container_instance)
            self.page.update()

            def loaded_callback():
                self.page.overlay.remove(app_container_instance)
                self.page.update()

            instance.load(self.page, self.page_back_func, plugin_dir, loaded_callback)
            
            # self.page.overlay.remove(app_container_instance)
            # self.page.update()
        self.page.update()

    def get_icon_base64(self, plugin_dir: str) -> str:
        with open(os.path.join(plugin_dir, "plugin.json"), 'r', encoding='utf-8') as f:
            plugin_info = json.load(f)
        icon_path = os.path.join(plugin_dir, plugin_info["icon"])
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_string

    def install_plugin(self, e: ft.FilePickerResultEvent, container: ft.Container) -> None:
        # プラグインを保存する一意のディレクトリを作成
        picked_file = e.files[0]
        picked_file_path = picked_file.path
        unique_key = str(uuid.uuid4())
        plugin_folder_name = picked_file.name[:-4] + unique_key  # ".zip"拡張子を除去してからunique_keyをつなげる
        plugin_dir = os.path.join(self.plugin_folder_path, plugin_folder_name)
        os.makedirs(plugin_dir, exist_ok=True)

        # ZIPファイルを解凍
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, picked_file.name)
                shutil.copy(picked_file_path, zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(plugin_dir)

            self.install_plugin_from_path(plugin_dir, container)
        except Exception as e:
            self.api.logger.error(f"Plugin installation failed: {e}")
            # インストールに失敗した場合は展開したフォルダを削除
            shutil.rmtree(plugin_dir, ignore_errors=True)

    def install_plugin_from_url(self, plugin_url: str):
        self.api.logger.info(f"install plugin from: {plugin_url} on PluginManager")
        try:
            # URLからプラグインをダウンロード
            response = requests.get(plugin_url)
            response.raise_for_status()

            # 一時ディレクトリにプラグインを保存
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name

            # 一時ディレクトリにプラグインを展開
            with tempfile.TemporaryDirectory() as temp_dir:
                with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # 展開されたプラグインのパスを取得
                plugin_dir = os.path.join(temp_dir, os.listdir(temp_dir)[0])

                # プラグインをインストール
                return self.process_plugin_installation(plugin_dir, self.myapp_container)

        except Exception as e:
            self.api.logger.error(f"Failed to install plugin from URL: {str(e)}")
            return False
        finally:
            # 一時ファイルを削除
            os.unlink(temp_file_path)

    def install_plugin_from_path(self, plugin_path: str, container: ft.Container):
        try:
            self.process_plugin_installation(plugin_path, container)
        except Exception as e:
            self.api.logger.error(f"Plugin installation failed: {e}")
            shutil.rmtree(plugin_path, ignore_errors=True)

    def process_plugin_installation(self, plugin_dir, container: ft.Container):
        with open(os.path.join(plugin_dir, "plugin.json"), 'r', encoding='utf-8') as f:
            plugin_info = json.load(f)

        plugin_name = plugin_info["plugin_name"]
        plugin_version = plugin_info["version"]

        if plugin_name in self.installed_plugins:
            return self.handle_plugin_overwrite(plugin_name, plugin_version, plugin_dir, container)
        else:
            self.complete_plugin_installation(plugin_dir, plugin_name, container)
            return True

    def handle_plugin_overwrite(self, plugin_name, new_version, plugin_dir, container: ft.Container):
        old_plugin_dir = self.installed_plugins[plugin_name]

        # 現在のバージョンを取得
        with open(os.path.join(old_plugin_dir, "plugin.json"), 'r', encoding='utf-8') as f:
            old_plugin_info = json.load(f)
        current_version = old_plugin_info["version"]

        result = None

        def overwrite_plugin(choice):
            nonlocal result
            result = choice == "yes"
            self.page.dialog.open = False
            self.page.update()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("上書きインストールの確認"),
            content=ft.Text(f"同じ名前のプラグイン '{plugin_name}' が既にインストールされています。\n現在のバージョン: {current_version}\n新しいバージョン: {new_version}\n\n上書きインストールしますか？"),
            actions=[
                ft.TextButton("はい", on_click=lambda _: overwrite_plugin("yes")),
                ft.TextButton("いいえ", on_click=lambda _: overwrite_plugin("no")),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = confirm_dialog
        self.page.dialog.open = True
        self.page.update()

        while result is None:
            self.page.update()

        if result:
            self.replace_plugin_files(old_plugin_dir, plugin_dir)
            try:
                if os.path.exists(plugin_dir):
                    shutil.rmtree(plugin_dir)
            except FileNotFoundError:
                pass
            self._load_plugin(old_plugin_dir, container)
        else:
            try:
                if os.path.exists(plugin_dir):
                    shutil.rmtree(plugin_dir)
            except FileNotFoundError:
                pass

        return result

    def complete_plugin_installation(self, plugin_dir, plugin_name, container: ft.Container):
        if not CodeSecurityScanner.scan_for_forbidden_functions(plugin_dir):
            self.api.logger.error("Security check failed: Forbidden functions found in the plugin code.")
            raise Exception("Security check failed: Forbidden functions found in the plugin code.")
        self.api.logger.info(f"Security check passed for plugin: {plugin_dir}")
        self._load_plugin(plugin_dir, container)
        self.installed_plugins[plugin_name] = plugin_dir

    def replace_plugin_files(self, old_plugin_dir, new_plugin_dir):
        for filename in os.listdir(old_plugin_dir):
            file_path = os.path.join(old_plugin_dir, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

        for filename in os.listdir(new_plugin_dir):
            src_path = os.path.join(new_plugin_dir, filename)
            dst_path = os.path.join(old_plugin_dir, filename)
            if os.path.isfile(src_path) or os.path.islink(src_path):
                shutil.copy2(src_path, dst_path)
            elif os.path.isdir(src_path):
                shutil.copytree(src_path, dst_path)

    def show_delete_confirmation(self, plugin_dir, unique_key) -> None:
        print("show_delete_confirmation called")
        def close_dlg(e) -> None:
            self.page.dialog.open = False
            self.page.update()
        
        delete_target = [plugin_dir, unique_key]
        dlg_modal = DeleteConfirmDialog("プラグインの削除", "このプラグインを削除してもよろしいですか？", "いいえ", "はい", close_dlg, self.delete_plugin, delete_target)
        self.page.dialog = dlg_modal.build()
        self.page.dialog.open = True
        self.page.update()

    def delete_plugin(self, del_target: list) -> None:
        self.api.logger.info("delete_plugin was called!")
        self.api.logger.info(del_target)
        plugin_dir = del_target[0]
        unique_key = del_target[1]
        self.api.logger.info(unique_key)

        def on_rm_error(func, path, exc_info) -> None:
            if exc_info[0] == FileNotFoundError:
                return
            import stat
            os.chmod(path, stat.S_IWRITE)
            os.unlink(path)

        shutil.rmtree(plugin_dir, onerror=on_rm_error)

        if unique_key in self.plugin_dict:
            ui_element = self.plugin_dict.pop(unique_key)
            if ui_element in self.myapp_container.controls:
                self.myapp_container.controls.remove(ui_element)
            else:
                self.api.logger.error("no ui element which matches unique_key")

            self.installed_plugins.pop(unique_key, None)
        else:
            self.api.logger.error(f"plugin not found in plugin_dict: {unique_key}")

        self.page.dialog.open = False
        self.page.update()

    def load_installed_plugins(self, container: ft.Container) -> None:
        self.plugin_dict = {}
        target_list = [filename for filename in os.listdir(self.plugin_folder_path) if not filename.startswith('.')]

        # 存在しないプラグインをself.installed_pluginsから削除する
        for plugin_name in list(self.installed_plugins.keys()):
            if plugin_name not in target_list:
                del self.installed_plugins[plugin_name]

        for plugin_name in target_list:
            self.api.logger.info(plugin_name)
            plugin_dir = os.path.join(self.plugin_folder_path, plugin_name)
            if os.path.isdir(plugin_dir):
                self._load_plugin(plugin_dir, container)
    
    def load_system_plugins(self, container: ft.Container) -> None:
        target_list = [filename for filename in os.listdir(self.system_plugin_folder_path) if not filename.startswith('.')]
        for plugin_name in target_list:
            self.api.logger.info(plugin_name)
            plugin_dir = os.path.join(self.system_plugin_folder_path, plugin_name)
            if os.path.isdir(plugin_dir):
                self._load_plugin(plugin_dir, container)
        plugin_management_proxy = self.intent_conductor.send_event("set_plugin_manager", self, sender_plugin=self.__class__.__name__, target_plugin="PluginManagementProxy")
        if plugin_management_proxy is not None:
            plugin_management_proxy.set_plugin_manager(self)
