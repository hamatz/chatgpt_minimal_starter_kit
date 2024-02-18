import base64
import zipfile
import os
import sys
import shutil
import json
import importlib
import flet as ft
from plugin_interface import PluginInterface
from ui_component_manager import UIComponentManager

PLUGIN_FOLDER = "installed_plugins"
TEMP_WORK_FOLDER = "temp"

class PluginManager:

    def __init__(self, page: ft.Page, page_back, ui_manager: UIComponentManager):
        self.page = page
        self.page_back_func = page_back
        self.__ui_manager = ui_manager
        if not os.path.exists(PLUGIN_FOLDER):
            os.makedirs(PLUGIN_FOLDER)
        if not os.path.exists(TEMP_WORK_FOLDER):
            os.makedirs(TEMP_WORK_FOLDER)

    def install_plugin(self, e: ft.FilePickerResultEvent, container: ft.Container) -> None:
        self.myapp_container = container
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
        plugin_instance = plugin_class(self.__ui_manager) 
        icon_path = os.path.join(extract_dir, plugin_info["icon"])
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        # アプリケーションのアイコンをUIに追加 
        app_icon = ft.Image(src_base64=encoded_string, width=100, height=100)
        # アイコンのクリックイベントにプラグインのUIビルド関数を関連付け
        clickable_image = ft.GestureDetector(
            content=app_icon,
            on_tap= lambda _: plugin_instance.load(self.page, self.page_back_func)
        )
        app_container_cmp = self.__ui_manager.get_component("app_container")
        app_title = plugin_info["name"]
        app_container_instance = app_container_cmp(app_title, clickable_image, "#ffffff", 5, 5)
        app_container_widget = app_container_instance.get_widget()
        deletable_app_container = ft.GestureDetector(
            content=app_container_widget,
            on_long_press_start= lambda e: self.show_delete_confirmation(plugin_dir, deletable_app_container)
        )
        #self.page.add(deletable_app_container)
        self.myapp_container.controls.append(deletable_app_container)
        self.page.update()
        # 削除ボタンの追加
        #delete_button = ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e: self.show_delete_confirmation(plugin_dir, [clickable_image, delete_button]))
        #self.page.controls.extend([clickable_image, delete_button])
        #self.page.update()

    def show_delete_confirmation(self, plugin_dir, ui_elements) -> None:

        def close_dlg(e) -> None:
            self.page.dialog.open = False
            self.page.update()

        dlg_component = self.__ui_manager.get_component("delete_confirm_daialog")
        delete_target = [plugin_dir, ui_elements]
        dlg_modal = dlg_component("プラグインの削除", "このプラグインを削除してもよろしいですか？", "いいえ", "はい", close_dlg, self.delete_plugin, delete_target)

        self.page.dialog = dlg_modal.get_widget()
        self.page.dialog.open = True
        self.page.update()

    def delete_plugin(self, del_target: list) -> None:
        print(del_target)
        plugin_dir = del_target[0]
        ui_elements = del_target[1]

        def on_rm_error(func, path, exc_info) -> None:
            import stat
            os.chmod(path, stat.S_IWRITE)
            os.unlink(path)
        # プラグインディレクトリを削除
        shutil.rmtree(plugin_dir, onerror=on_rm_error)
        # UIからプラグイン関連の要素を削除
        #for element in ui_elements:
        self.myapp_container.controls.remove(ui_elements)
        # 削除確認ダイアログを閉じる
        self.page.dialog.open = False
        self.page.update()

    def load_installed_plugins(self, container: ft.Container) -> None:
        self.myapp_container = container
        for plugin_name in os.listdir(PLUGIN_FOLDER):
            plugin_dir = os.path.join(PLUGIN_FOLDER, plugin_name)
            if os.path.isdir(plugin_dir):
                # プラグインのメタデータを読み込み
                with open(os.path.join(plugin_dir, "plugin.json"), 'r') as f:
                    plugin_info = json.load(f)
                sys.path.append(plugin_dir)
                # プラグインモジュールを動的にインポート
                plugin_module = importlib.import_module(plugin_info["main_module"])
                plugin_class = getattr(plugin_module, plugin_info["plugin_name"])
                plugin_instance = plugin_class(self.__ui_manager) 
                icon_path = os.path.join(plugin_dir, plugin_info["icon"])
                with open(icon_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                # アプリケーションのアイコンをUIに追加 
                app_icon = ft.Image(src_base64=encoded_string, width=100, height=100)
                # アイコンのクリックイベントにプラグインのUIビルド関数を関連付け
                clickable_image = ft.GestureDetector(
                    content=app_icon,
                    on_tap= lambda _: plugin_instance.load(self.page, self.page_back_func)
                )
                app_container_cmp = self.__ui_manager.get_component("app_container")
                app_title = plugin_info["name"]
                app_container_instance = app_container_cmp(app_title, clickable_image, "#ffffff", 5, 5)
                app_container_widget = app_container_instance.get_widget()
                deletable_app_container = ft.GestureDetector(
                    content=app_container_widget,
                    on_long_press_start= lambda e: self.show_delete_confirmation(plugin_dir, deletable_app_container)
                )
                #self.page.add(deletable_app_container)
                self.myapp_container.controls.append(deletable_app_container)

        self.page.update()
