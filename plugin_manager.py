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
from typing import Callable
from interfaces.plugin_interface import PluginInterface
from interfaces.system_plugin_interface import SystemPluginInterface
from ui_component_manager import UIComponentManager
from intent_conductor import IntentConductor
from system_api_layer import SystemAPI
from api import API
from code_security_scanner import CodeSecurityScanner

PLUGIN_FOLDER = "installed_plugins"
SYSTEM_PLUGIN_FOLDER = "system"

class PluginManager:

    def __init__(self, page: ft.Page, page_back : Callable[[], None], ui_manager: UIComponentManager, system_api: SystemAPI, base_dir: str, save_dir: str, api : API, intent_conductor: IntentConductor):
        self.page = page
        self.page_back_func = page_back
        self.plugin_dict = {}
        self.__ui_manager = ui_manager
        self.__system_api = system_api
        self.api = api
        self.intent_conductor = intent_conductor
        self.plugin_folder_path = os.path.join(save_dir, PLUGIN_FOLDER)
        self.system_plugin_folder_path = os.path.join(base_dir, SYSTEM_PLUGIN_FOLDER)
        self.myapp_container = None
        if not os.path.exists(self.plugin_folder_path):
            os.makedirs(self.plugin_folder_path)
        if not os.path.exists(self.system_plugin_folder_path):
            os.makedirs(self.system_plugin_folder_path)

    def _load_plugin(self, plugin_dir: str, container: ft.Container):
        try:
            with open(os.path.join(plugin_dir, "plugin.json"), 'r', encoding='utf-8') as f:
                plugin_info = json.load(f)
        except UnicodeDecodeError as e:
            self.api.logger.error(f"Error decoding plugin.json: {e}")
            return  # エラー時は処理を中断
        sys.path.append(plugin_dir)
        plugin_module = importlib.import_module(plugin_info["main_module"])
        plugin_class = getattr(plugin_module, plugin_info["plugin_name"])
        # システムプラグインかどうかに基づき、インスタンスを作成
        if "system" in plugin_dir:
            plugin_instance = plugin_class(self.__system_api, self.intent_conductor)
        else:
            plugin_instance = plugin_class(self.intent_conductor)
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
            on_tap=lambda _, instance=plugin_instance, extract_dir=plugin_dir: instance.load(self.page, self.page_back_func, extract_dir, self.api)
        )
        app_container_cmp = self.__ui_manager.get_component("app_container")
        app_title = plugin_info["name"]
        app_version = "Version: " + plugin_info["version"]
        app_container_instance = app_container_cmp(app_title, app_version, clickable_image, "#ffffff" if "system" not in plugin_dir else "#20b2aa")
        app_container_widget = app_container_instance.get_widget()

        if "system" in plugin_dir:
            container.controls.append(app_container_widget)
        else:
            unique_key = str(uuid.uuid4())
            deletable_app_container = ft.GestureDetector(
                content=app_container_widget,
                on_long_press_start=lambda e: self.show_delete_confirmation(plugin_dir, unique_key)
            )
            container.controls.append(deletable_app_container)
            self.myapp_container = container
            self.plugin_dict[unique_key] = deletable_app_container
        self.page.update()

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
            # セキュリティスキャンを実行
            if not CodeSecurityScanner.scan_for_forbidden_functions(plugin_dir):
                 self.api.logger.error("Security check failed: Forbidden functions found in the plugin code.")
                 raise Exception("Security check failed: Forbidden functions found in the plugin code.")
            self.api.logger.info(f"Security check passed for plugin: {plugin_dir}")
            self._load_plugin(plugin_dir, container)

        except Exception as e:
            self.api.logger.error(f"Plugin installation failed: {e}")
            # インストールに失敗した場合は展開したフォルダを削除
            shutil.rmtree(plugin_dir, ignore_errors=True)
            return

    def show_delete_confirmation(self, plugin_dir, unique_key) -> None:

        def close_dlg(e) -> None:
            self.page.dialog.open = False
            self.page.update()
        
        dlg_component = self.__ui_manager.get_component("delete_confirm_dialog")
        delete_target = [plugin_dir, unique_key]
        dlg_modal = dlg_component("プラグインの削除", "このプラグインを削除してもよろしいですか？", "いいえ", "はい", close_dlg, self.delete_plugin, delete_target)
        self.page.dialog = dlg_modal.get_widget()
        self.page.dialog.open = True
        self.page.update()

    def delete_plugin(self, del_target: list) -> None:
        self.api.logger.info("delete_plugin was called!")
        self.api.logger.info(del_target)
        plugin_dir = del_target[0]
        unique_key = del_target[1]
        self.api.logger.info(unique_key)

        def on_rm_error(func, path, exc_info) -> None:
            import stat
            os.chmod(path, stat.S_IWRITE)
            os.unlink(path)
        # プラグインディレクトリを削除
        shutil.rmtree(plugin_dir, onerror=on_rm_error)
        # UIからプラグイン関連の要素を削除
        if unique_key in self.plugin_dict:
            ui_element = self.plugin_dict.pop(unique_key)
            if ui_element in self.myapp_container.controls:
                self.myapp_container.controls.remove(ui_element)
            else:
                self.api.logger.error("no ui element which matches unique_key")
        # 削除確認ダイアログを閉じる
        self.page.dialog.open = False
        self.page.update()

    def load_installed_plugins(self, container: ft.Container) -> None:
        self.plugin_dict = {}
        target_list = [filename for filename in os.listdir(self.plugin_folder_path) if not filename.startswith('.')]
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
