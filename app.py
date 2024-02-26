import json
import os
import sys
import flet as ft
from plugin_manager import PluginManager
from my_key_manager import MyKeyManager
from ui_component_manager import UIComponentManager
from system_file_controller import SystemFileController
from system_api_layer import SystemAPI
from api import API
from ui_components.password_dialog import PasswordDialog
from ui_components.delete_confirm_dialog import DeleteConfirmDialog
from ui_components.simple_header import SimpleHeader
from ui_components.simple_header_2 import SimpleHeader2
from ui_components.simple_footer import SimpleFooter
from ui_components.app_container import AppContainer

MY_SYSTEM_NAME = "CraftForgeBase"
SYSTEM_FILENAME = "system_shared_data.json"
VERSION = "0.1.0"
BUILD_NUMBER = "1"
MY_KEY_FILENAME = "my_app_info.json"
HAKONIWA = False

class CraftForgeBase:
    def __init__(self, page: ft.Page, base_dir :str , save_dir: str) -> None:
        self.page = page
        self.page.title = MY_SYSTEM_NAME
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.ui_manager = UIComponentManager()
        self.ui_manager.add_component("password_daialog", PasswordDialog)
        self.ui_manager.add_component("delete_confirm_daialog", DeleteConfirmDialog)
        self.ui_manager.add_component("simple_header", SimpleHeader)
        self.ui_manager.add_component("simple_header2", SimpleHeader2)
        self.ui_manager.add_component("simple_footer", SimpleFooter)
        self.ui_manager.add_component("app_container", AppContainer)
        self.mkm = MyKeyManager(self.page, self.ui_manager, base_dir, MY_KEY_FILENAME)
        self.system_fc = SystemFileController(SYSTEM_FILENAME, base_dir)
        self.system_api = SystemAPI(self.mkm, self.system_fc)
        self.api = API(self.system_api)
        self.pm = PluginManager(self.page, self.page_back, self.ui_manager, self.system_api, base_dir, save_dir, self.api)
        self.mkm.load_my_key()

    def show_main_page(self) -> None:
        def pick_file_and_install(e: ft.FilePickerResultEvent):
            self.pm.install_plugin(e, main_container)

        self.page.appbase_toast =  ft.SnackBar(
            content=ft.Text("appbase_toast"),
            action="Alright!",
        )
        my_header_cmp = self.ui_manager.get_component("simple_header")
        my_header_instance = my_header_cmp(ft.icons.MENU_ROUNDED, "CraftForge v.0.0.1", "#20b2aa")
        my_header_widget = my_header_instance.get_widget()
        my_footer_cmp = self.ui_manager.get_component("simple_footer")
        my_footer_instance = my_footer_cmp("@hamatz", "#20b2aa")
        my_footer_widget = my_footer_instance.get_widget()
        self.page.add(my_header_widget)
        main_container = ft.GridView(
            expand=1,
            runs_count=5,
            max_extent=120,
            child_aspect_ratio=1.0,
            spacing=5,
            run_spacing=5,
        )
        self.page.add(main_container)
        self.pm.load_installed_plugins(main_container)
        self.pm.load_system_plugins(main_container)
        file_picker = ft.FilePicker(on_result=pick_file_and_install)
        self.page.overlay.append(file_picker)
        install_button = ft.ElevatedButton("Install Plugin", icon=ft.icons.UPLOAD_FILE, on_click=lambda _:file_picker.pick_files())
        self.page.add(install_button, my_footer_widget)
        self.page.update()

    def page_back(self) -> None:
        self.page.clean()
        self.show_main_page()

def main(page: ft.Page) -> None:
    # アプリケーションが実行されているディレクトリを取得
    if getattr(sys, 'frozen', False):
        # アプリケーションがPyInstallerによってパッケージされている場合
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    #新規ログインかどうかの確認
    my_key_file_path = os.path.join(base_dir, MY_KEY_FILENAME)
    is_key_file = os.path.isfile(my_key_file_path)

    if is_key_file:
        # トリッキーなので本当は直接このファイルを触りたくないがCraftForgeBase初期化前にパスを知らねばなので...
        system_file_path = os.path.join(base_dir, SYSTEM_FILENAME)
        with open(system_file_path, 'rb') as f:
            my_key_file = json.load(f)
            my_settings_info = my_key_file.get(MY_SYSTEM_NAME, {}).get("settings")
            my_save_dir = my_settings_info.get("my_save_path")
        if HAKONIWA:
            app = CraftForgeBase(page, base_dir , base_dir)
            app.system_fc.save_system_dict(MY_SYSTEM_NAME, "app_info",
                                        {"version" : VERSION, 
                                        "build_number" : BUILD_NUMBER})
            app.show_main_page()
        else:
            app = CraftForgeBase(page, base_dir , my_save_dir)
            app.system_fc.save_system_dict(MY_SYSTEM_NAME, "app_info",
                                        {"version" : VERSION, 
                                        "build_number" : BUILD_NUMBER})
            app.show_main_page()
    else:
        if HAKONIWA:
            app = CraftForgeBase(page, base_dir , base_dir)
            app.system_fc.save_system_dict(MY_SYSTEM_NAME, "app_info",
                                        {"version" : VERSION, 
                                        "build_number" : BUILD_NUMBER})
            app.system_fc.save_system_dict(MY_SYSTEM_NAME, "settings",
                                        {"my_save_path" : base_dir})
            app.show_main_page()
        else:
            def on_dialog_result(e: ft.FilePickerResultEvent):
                save_dir=e.path
                page.overlay.remove(file_picker)
                page.remove(select_dir_button)
                page.clean()
                page.update()
                app = CraftForgeBase(page, base_dir , save_dir)
                app.system_fc.save_system_dict(MY_SYSTEM_NAME, "app_info",
                                            {"version" : VERSION, 
                                            "build_number" : BUILD_NUMBER})
                app.system_fc.save_system_dict(MY_SYSTEM_NAME, "settings",
                                            {"my_save_path" : save_dir})
                app.show_main_page()

            def on_button_click(_):
                page.overlay.append(file_picker)
                page.update()
                file_picker.get_directory_path()
            # 保存先選択ボタン
            select_dir_button = ft.ElevatedButton(
                "本システムの利用する保存先のフォルダを選択してください",
                on_click=on_button_click
            )
            page.add(select_dir_button)
            file_picker = ft.FilePicker(on_result=on_dialog_result)
            page.overlay.append(file_picker)
            page.update()

if __name__ == "__main__":
    ft.app(target=main)