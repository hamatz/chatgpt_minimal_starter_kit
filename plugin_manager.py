import base64
import uuid
import zipfile
import os
import sys
import shutil
import json
import importlib
import flet as ft
from typing import Callable
from plugin_interface import PluginInterface
from system_plugin_interface import SystemPluginInterface
from ui_component_manager import UIComponentManager
from system_api_layer import SystemAPI

PLUGIN_FOLDER = "installed_plugins"
SYSTEM_PLUGIN_FOLDER = "system"
TEMP_WORK_FOLDER = "temp"

class PluginManager:

    def __init__(self, page: ft.Page, page_back : Callable[[], None], ui_manager: UIComponentManager, system_api: SystemAPI):
        self.page = page
        self.page_back_func = page_back
        self.plugin_dict = {}
        self.__ui_manager = ui_manager
        self.__system_api = system_api
       #self.__system_fc = system_fc
        if not os.path.exists(PLUGIN_FOLDER):
            os.makedirs(PLUGIN_FOLDER)
        if not os.path.exists(TEMP_WORK_FOLDER):
            os.makedirs(TEMP_WORK_FOLDER)
        if not os.path.exists(SYSTEM_PLUGIN_FOLDER):
            os.makedirs(SYSTEM_PLUGIN_FOLDER)

    def install_plugin(self, e: ft.FilePickerResultEvent, container: ft.Container) -> None:
        # プラグインを保存する一意のディレクトリを作成
        picked_file = e.files[0]
        picked_file_path = picked_file.path
        plugin_dir = os.path.join(PLUGIN_FOLDER, picked_file.name[:-4])  # ".zip"拡張子を除去
        os.makedirs(plugin_dir, exist_ok=True)
        # ZIPファイルを一時ディレクトリに保存
        zip_path = os.path.join("temp", picked_file.name)
        shutil.copy(picked_file_path, zip_path)
        # ZIPファイルを解凍するディレクトリを指定
        extract_dir = os.path.join(PLUGIN_FOLDER, picked_file.name[:-4])
        # ZIPファイルを解凍
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        # メタデータファイルを読み込み（例えば "plugin.json"）
        with open(os.path.join(extract_dir, "plugin.json"), 'r') as f:
            plugin_info = json.load(f)
        print(plugin_info)
        sys.path.append(extract_dir)
        # プラグインモジュールを動的にインポート
        plugin_module = importlib.import_module(plugin_info["main_module"])
        print(plugin_module)
        plugin_class = getattr(plugin_module, plugin_info["plugin_name"])
        print(plugin_class)
        plugin_instance = plugin_class(self.__ui_manager) 
        icon_path = os.path.join(extract_dir, plugin_info["icon"])
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        # アプリケーションのアイコンをUIに追加 
        app_icon = ft.Image(src_base64=encoded_string, width=100, height=100)
        # アイコンのクリックイベントにプラグインのUIビルド関数を関連付け
        clickable_image = ft.GestureDetector(
            content=app_icon,
            on_tap= lambda _, instance=plugin_instance, extract_dir=extract_dir: instance.load(self.page, self.page_back_func, extract_dir)
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
        target_list = [filename for filename in os.listdir(PLUGIN_FOLDER) if not filename.startswith('.')]
        for plugin_name in target_list:
            print(plugin_name)
            plugin_dir = os.path.join(PLUGIN_FOLDER, plugin_name)
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
                    on_tap= lambda _, instance=plugin_instance, plugin_dir=plugin_dir: instance.load(self.page, self.page_back_func, plugin_dir)
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
                #print(container.controls)
                
        self.myapp_container = container
        self.page.update()
    
    def load_system_plugins(self, container: ft.Container) -> None:
        target_list = [filename for filename in os.listdir(SYSTEM_PLUGIN_FOLDER) if not filename.startswith('.')]
        for plugin_name in target_list:
            print(plugin_name)
            plugin_dir = os.path.join(SYSTEM_PLUGIN_FOLDER, plugin_name)
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
                    on_tap= lambda _, instance=system_plugin_instance, plugin_dir=plugin_dir: instance.load(self.page, self.page_back_func, plugin_dir)
                )
                system_app_container_cmp = self.__ui_manager.get_component("app_container")
                app_title = plugin_info["name"]
                system_app_container_instance = system_app_container_cmp(app_title, clickable_image, "#657564")
                system_app_container_widget = system_app_container_instance.get_widget()
                container.controls.append(system_app_container_widget)
                
        self.myapp_container = container
        self.page.update()       
