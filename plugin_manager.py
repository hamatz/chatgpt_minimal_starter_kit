import ast
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
from system_api_layer import SystemAPI
from api import API

PLUGIN_FOLDER = "installed_plugins"
SYSTEM_PLUGIN_FOLDER = "system"

class PluginManager:

    def __init__(self, page: ft.Page, page_back : Callable[[], None], ui_manager: UIComponentManager, system_api: SystemAPI, base_dir: str, save_dir: str, api : API):
        self.page = page
        self.page_back_func = page_back
        self.plugin_dict = {}
        self.__ui_manager = ui_manager
        self.__system_api = system_api
        self.api = api
        self.plugin_folder_path = os.path.join(save_dir, PLUGIN_FOLDER)
        self.system_plugin_folder_path = os.path.join(base_dir, SYSTEM_PLUGIN_FOLDER)
        if not os.path.exists(self.plugin_folder_path):
            os.makedirs(self.plugin_folder_path)
        if not os.path.exists(self.system_plugin_folder_path):
            os.makedirs(self.system_plugin_folder_path)

    def scan_for_forbidden_functions(folder_path):
        forbidden_code_found = False

        class ForbiddenFunctionFinder(ast.NodeVisitor):
            def __init__(self):
                self.forbidden_os_functions = {
                    "os": ["system", "popen", "execl", "execle", "execlp", "execlpe", "execv", "execve", "execvp", "execvpe", "open", "remove", "unlink", "rmdir", "removedirs", "rename", "walk"]
                }
                self.danger_functions = ["eval", "exec", "open", "__import__"]

            def visit_Import(self, node):
                for alias in node.names:
                    if alias.name in self.forbidden_os_functions or alias.name in self.danger_functions:
                        nonlocal forbidden_code_found
                        forbidden_code_found = True
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                if node.module in self.forbidden_os_functions or node.module in self.danger_functions:
                    nonlocal forbidden_code_found
                    forbidden_code_found = True
                self.generic_visit(node)

            def visit_Call(self, node):
                if (isinstance(node.func, ast.Attribute) and 
                    node.func.attr in self.forbidden_os_functions.get(getattr(node.func.value, 'id', ''), [])) or \
                    (isinstance(node.func, ast.Name) and node.func.id in self.danger_functions):
                    nonlocal forbidden_code_found
                    forbidden_code_found = True
                self.generic_visit(node)

        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r") as source_file:
                        tree = ast.parse(source_file.read(), filename=file_path)
                        finder = ForbiddenFunctionFinder()
                        finder.visit(tree)
                        if forbidden_code_found:
                            # 悪意のあるコードが見つかったら、すぐに False を返してスキャンを終了する
                            return False
        # 悪意のあるコードが見つからなければ True を返す
        return True

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
            with tempfile.TemporaryDirectory(dir=plugin_dir) as temp_dir:
                zip_path = os.path.join(temp_dir, picked_file.name)
                shutil.copy(picked_file_path, zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(plugin_dir)
                    # セキュリティスキャンを実行
            if not self.scan_for_forbidden_functions(plugin_dir):
                raise Exception("Security check failed: Forbidden functions found in the plugin code.")
            # メタデータファイルを読み込み（例えば "plugin.json"）
            with open(os.path.join(plugin_dir, "plugin.json"), 'r') as f:
                plugin_info = json.load(f)
            print(plugin_info)
            sys.path.append(plugin_dir)
            # プラグインモジュールを動的にインポート
            plugin_module = importlib.import_module(plugin_info["main_module"])
            print(plugin_module)
            plugin_class = getattr(plugin_module, plugin_info["plugin_name"])
            print(plugin_class)
            plugin_instance = plugin_class(self.__ui_manager) 
            icon_path = os.path.join(plugin_dir, plugin_info["icon"])
            with open(icon_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            # アプリケーションのアイコンをUIに追加 
            app_icon = ft.Image(src_base64=encoded_string, width=100, height=100)
            # アイコンのクリックイベントにプラグインのUIビルド関数を関連付け
            clickable_image = ft.GestureDetector(
                content=app_icon,
                on_tap= lambda _, instance=plugin_instance, extract_dir=plugin_dir: instance.load(self.page, self.page_back_func, extract_dir, self.api)
            )
            app_container_cmp = self.__ui_manager.get_component("app_container")
            app_title = plugin_info["name"]
            app_container_instance = app_container_cmp(app_title, clickable_image, "#ffffff")
            app_container_widget = app_container_instance.get_widget()
            unique_key = str(uuid.uuid4())
            deletable_app_container = ft.GestureDetector(
                content=app_container_widget,
                on_long_press_start= lambda e: self.show_delete_confirmation(plugin_dir, unique_key)
                )
            container.controls.append(deletable_app_container)
            self.myapp_container = container
            self.plugin_dict[unique_key] = deletable_app_container
            self.page.update()
        except Exception as e:
            print(f"Plugin installation failed: {e}")
            # インストールに失敗した場合は展開したフォルダを削除
            shutil.rmtree(plugin_dir, ignore_errors=True)
            return

    def show_delete_confirmation(self, plugin_dir, unique_key) -> None:

        def close_dlg(e) -> None:
            self.page.dialog.open = False
            self.page.update()

        dlg_component = self.__ui_manager.get_component("delete_confirm_daialog")
        delete_target = [plugin_dir, unique_key]
        dlg_modal = dlg_component("プラグインの削除", "このプラグインを削除してもよろしいですか？", "いいえ", "はい", close_dlg, self.delete_plugin, delete_target)

        self.page.dialog = dlg_modal.get_widget()
        self.page.dialog.open = True
        self.page.update()

    def delete_plugin(self, del_target: list) -> None:
        print("delete_plugin was called!")
        print(del_target)
        plugin_dir = del_target[0]
        unique_key = del_target[1]
        print(unique_key)

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
                print("no ui element which matches unique_key")
        # 削除確認ダイアログを閉じる
        self.page.dialog.open = False
        self.page.update()

    def load_installed_plugins(self, container: ft.Container) -> None:
        self.plugin_dict = {}
        #self.myapp_container = container
        target_list = [filename for filename in os.listdir(self.plugin_folder_path) if not filename.startswith('.')]
        for plugin_name in target_list:
            print(plugin_name)
            plugin_dir = os.path.join(self.plugin_folder_path, plugin_name)
            if os.path.isdir(plugin_dir):
                # プラグインのメタデータを読み込み
                with open(os.path.join(plugin_dir, "plugin.json"), 'r') as f:
                    plugin_info = json.load(f)
                sys.path.append(plugin_dir)
                # モジュールのファイルパスを指定
                module_path = os.path.join(plugin_dir, plugin_info["main_module"] + ".py")  # モジュールファイル名に.pyを追加
                # モジュール仕様を作成
                spec = importlib.util.spec_from_file_location(plugin_info["plugin_name"], module_path)
                if spec is not None:
                    # モジュールオブジェクトを作成
                    plugin_module = importlib.util.module_from_spec(spec)
                    print(plugin_module)
                    # モジュール内のコードを実行
                    spec.loader.exec_module(plugin_module)
                    # プラグインクラスを取得
                    plugin_class = getattr(plugin_module, plugin_info["plugin_name"])
                    print(plugin_class)

                plugin_instance = plugin_class(self.__ui_manager) 
                print(plugin_instance)
                icon_path = os.path.join(plugin_dir, plugin_info["icon"])
                with open(icon_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                # アプリケーションのアイコンをUIに追加 
                app_icon = ft.Image(src_base64=encoded_string, width=100, height=100)
                # アイコンのクリックイベントにプラグインのUIビルド関数を関連付け
                clickable_image = ft.GestureDetector(
                    content=app_icon,
                    on_tap= lambda _, instance=plugin_instance, plugin_dir=plugin_dir: instance.load(self.page, self.page_back_func, plugin_dir, self.api)
                )
                app_container_cmp = self.__ui_manager.get_component("app_container")
                app_title = plugin_info["name"]
                app_container_instance = app_container_cmp(app_title, clickable_image, "#ffffff")
                app_container_widget = app_container_instance.get_widget()
                unique_key = str(uuid.uuid4())
                def make_deletable_app_container(plugin_dir, unique_key):
                    return ft.GestureDetector(
                        content=app_container_widget,
                        on_long_press_start=lambda e, plugin_dir=plugin_dir, app_container=unique_key: self.show_delete_confirmation(plugin_dir, app_container)
                    )
                deletable_app_container = make_deletable_app_container(plugin_dir, unique_key)
                self.plugin_dict[unique_key] = deletable_app_container
                container.controls.append(deletable_app_container)
                
        self.myapp_container = container
        self.page.update()
    
    def load_system_plugins(self, container: ft.Container) -> None:
        target_list = [filename for filename in os.listdir(self.system_plugin_folder_path) if not filename.startswith('.')]
        for plugin_name in target_list:
            print(plugin_name)
            plugin_dir = os.path.join(self.system_plugin_folder_path, plugin_name)
            if os.path.isdir(plugin_dir):
                with open(os.path.join(plugin_dir, "plugin.json"), 'r') as f:
                    plugin_info = json.load(f)
                sys.path.append(plugin_dir)
                module_path = os.path.join(plugin_dir, plugin_info["main_module"] + ".py")
                spec = importlib.util.spec_from_file_location(plugin_info["plugin_name"], module_path)
                if spec is not None:
                    plugin_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(plugin_module)
                    plugin_class = getattr(plugin_module, plugin_info["plugin_name"])
                #システム権限があるプラグインはシステム鍵とシステム共通のファイルが使えるようになる
                system_plugin_instance = plugin_class(self.__ui_manager, self.__system_api) 
                icon_path = os.path.join(plugin_dir, plugin_info["icon"])
                with open(icon_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                app_icon = ft.Image(src_base64=encoded_string, width=100, height=100)
                clickable_image = ft.GestureDetector(
                    content=app_icon,
                    on_tap= lambda _, instance=system_plugin_instance, plugin_dir=plugin_dir: instance.load(self.page, self.page_back_func, plugin_dir, self.api)
                )
                system_app_container_cmp = self.__ui_manager.get_component("app_container")
                app_title = plugin_info["name"]
                system_app_container_instance = system_app_container_cmp(app_title, clickable_image, "#657564")
                system_app_container_widget = system_app_container_instance.get_widget()
                container.controls.append(system_app_container_widget)
                
        self.myapp_container = container
        self.page.update()       
