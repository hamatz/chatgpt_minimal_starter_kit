import base64
import json
import os
import uuid
import flet as ft
from system_plugin_interface import SystemPluginInterface
from typing import Callable
from ui_component_manager import UIComponentManager
from system_api_layer import SystemAPI


class SettingsPlugin(SystemPluginInterface):

    _instance = None
    
    def __new__(cls, ui_manager : UIComponentManager, system_api : SystemAPI):
        if cls._instance is None:
            cls._instance = super(SettingsPlugin, cls).__new__(cls)
            cls._instance.ui_manager = ui_manager
            cls._instance.system_api = system_api
        return cls._instance

    def show_toast(e, page: ft.Page, message: str) -> None:
        page.snack_bar = ft.SnackBar(ft.Text(message))
        page.snack_bar.open = True
        page.update()

    def load(self, page: ft.Page, function_to_top_page : Callable[[],None], plugin_dir_path: str):
        MY_SYSTEM_NAME = "CraftForgeBase"
        MY_APP_NAME = "System_Settings"
        page.clean()
        my_header_cmp = self.ui_manager.get_component("simple_header2")
        icon_path = os.path.join(plugin_dir_path, "back_button.png")
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            app_icon = ft.Image(src_base64=encoded_string, width=30, height=30)
        clickable_icon = ft.GestureDetector(
            content=app_icon,
            on_tap= lambda _: function_to_top_page()
        )
        my_header_instance = my_header_cmp(clickable_icon, MY_APP_NAME, "#20b2aa")
        my_header_widget = my_header_instance.get_widget()
        page.add(my_header_widget)

        def show_delete_confirmation(e: ft.ControlEvent, panel: ft.ExpansionPanelList, target_title: str) -> None:

            def close_dlg(e) -> None:
                self.page.dialog.open = False
                self.page.update()

            dlg_component = self.__ui_manager.get_component("delete_confirm_daialog")
            delete_target = [panel, target_title]
            dlg_modal = dlg_component(target_title, "設定情報を削除します。よろしいですか？", "いいえ", "はい", close_dlg, handle_delete, delete_target)

            self.page.dialog = dlg_modal.get_widget()
            self.page.dialog.open = True
            self.page.update()

        def handle_delete(e: ft.ControlEvent, target: list):
            target_panel = self.settings_info_dict[target[0]]
            target_item_title = self.settings_info_dict[target[1]]
            result = self.system_api.delete_system_data(MY_APP_NAME, target_item_title)
            if result:
                target_panel.controls.remove(e.control.data)
                load_system_info()
                page.update()
            else:
                self.show_toast(e, page, "削除処理に失敗しました")

        def load_system_info():
            system_data_dict = self.system_api.get_system_dicts_all()
            self.settings_info_dict = system_data_dict.get(MY_APP_NAME, {})

            # settings_info_dictが空の場合、初期設定用のJSONデータを読み込む
            if not self.settings_info_dict:
                json_path = os.path.join(plugin_dir_path, 'initial_settings.json')
                with open(json_path, 'r', encoding='utf-8') as f:
                    initial_settings = json.load(f)
                    self.settings_info_dict = initial_settings

            my_system_info = system_data_dict.get(MY_SYSTEM_NAME, {}).get("app_info", {})
            my_version = "Version : " + my_system_info.get("version", "不明")
            my_build_num = my_system_info.get("build_number", "不明")
            my_version_info = my_version + " (" + my_build_num + ")"
            print(my_version_info)

            panel = ft.ExpansionPanelList(
                expand_icon_color=ft.colors.AMBER,
                elevation=8,
                divider_color=ft.colors.AMBER,
                controls=[],
            )

            if self.settings_info_dict:
                for service_name, settings in self.settings_info_dict.items():
                    title = service_name
                    setting_info = settings

                    # 各設定項目を含むコンテナを作成
                    content_container = ft.Column([])
                    for prop_name, desc in setting_info.items():
                        list_tile = ft.ListTile(
                            title=ft.Text(prop_name),
                            subtitle=ft.Text(desc),
                            trailing=ft.IconButton(ft.icons.DELETE, on_click=lambda e, panel=panel, title=title: show_delete_confirmation(e, panel, title)),
                        )
                        content_container.controls.append(list_tile)

                    exp = ft.ExpansionPanel(
                        bgcolor=ft.colors.BLUE_100,
                        header=ft.ListTile(title=ft.Text(title)),
                        content=content_container, 
                    )
                    panel.controls.append(exp)
            page.add(panel)

        load_system_info()
        page.update()
