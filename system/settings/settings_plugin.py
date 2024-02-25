import base64
import json
import os
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

        def change_edit_mode(e: ft.ControlEvent, tile: ft.ListTile) -> None:
            tile.title.disabled = not tile.title.disabled  # テキストフィールドのdisabled属性を反転
            if tile.title.disabled:
                tile.trailing.icon = ft.icons.EDIT  # 編集不可状態なら編集アイコンに
            else:
                tile.trailing.icon = ft.icons.SAVE  # 編集可能状態なら保存アイコンに
            page.update()

        def save_data(e, tile, service_name: str, prop_name: str,  is_secure: bool):
            settings_info_dict = self.settings_info_dict.copy()
            target_dict = settings_info_dict.get(service_name, {})
            edited_data = tile.title.value
            if is_secure:
                target_data = self.system_api.encrypt_system_data(edited_data)
                tile.title.value = target_data  # UI上で暗号化された値を表示する必要があるかどうかは要検討。今のところは一度設定したら見えない方が安全なのでは？という方針
            else:
                target_data = edited_data
            
            ui_type = "description" if prop_name == "description" else "text"
            target_dict[prop_name] = {"value": target_data, "ui_type": ui_type, "is_encrypted": is_secure}

            self.system_api.save_system_dict(MY_APP_NAME, service_name, target_dict)
            self.settings_info_dict = self.system_api.get_system_dicts_all()
            change_edit_mode(e, tile)  # 編集モードを切り替えて編集不可状態に戻す

        def load_system_info():
            system_data_dict = self.system_api.get_system_dicts_all()
            self.settings_info_dict = system_data_dict.get(MY_APP_NAME, {})
            # settings_info_dictが空の場合、初期設定用のJSONデータを読み込む
            if not self.settings_info_dict:
                json_path = os.path.join(plugin_dir_path, 'initial_settings.json')
                with open(json_path, 'r', encoding='utf-8') as f:
                    initial_settings = json.load(f)
                    for service_name, settings in initial_settings.items():
                        title = service_name
                        setting_info = settings
                        self.system_api.save_system_dict(MY_APP_NAME, service_name, setting_info)
                    self.settings_info_dict = initial_settings

            my_system_info = system_data_dict.get(MY_SYSTEM_NAME, {}).get("app_info", {})
            my_version = "Version  " + my_system_info.get("version", "不明")
            my_build_num = my_system_info.get("build_number", "不明")
            my_version_info = my_version + " (" + my_build_num + ")"

            app_icon_path = os.path.join(plugin_dir_path, "app_icon.png")
            with open(app_icon_path, "rb") as app_image_file:
                encoded_image_string = base64.b64encode(app_image_file.read()).decode("utf-8")
                my_app_icon = ft.Image(src_base64=encoded_image_string, width=45, height=45,  fit="contain")
            title_bar = ft.ListTile(
                leading=my_app_icon,
                title=ft.Text("CraftForge" + "   " + my_version_info),
            )
            page.add(title_bar)

            scrollable_container = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

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
                    content_container = ft.Column([])
                    is_secure_data = settings.get("is_encrypted", {}).get("value", False)
                    for prop_name, values  in setting_info.items():
                        ui_type = values.get("ui_type")
                        is_not_editable = True
                        if ui_type == "text":
                            tmp_title=ft.TextField(label=prop_name, disabled=is_not_editable, value=values.get("value"))
                            list_tile = ft.ListTile(
                                title=tmp_title,
                            )
                            list_tile.trailing = ft.IconButton(ft.icons.EDIT, on_click=lambda e, tile=list_tile, s_name=service_name, p_name=prop_name,  is_secure=is_secure_data: save_data(e, tile, s_name, p_name, is_secure) if not tile.title.disabled else change_edit_mode(e, tile))
                        elif ui_type == "toggle":
                             list_tile = ft.ListTile(
                                title=ft.Text(prop_name),
                                subtitle=ft.Switch(label=is_secure_data, value=is_secure_data, disabled=True),
                            )
                        elif ui_type == "description": #利便性を考えるとdescription自体は常に暗号化されないべきなので is_secureの設定を無視する
                            tmp_title=ft.TextField(label=prop_name, disabled=is_not_editable, value=values.get("value"))
                            list_tile = ft.ListTile(
                                title=tmp_title,
                            )
                            list_tile.trailing = ft.IconButton(ft.icons.EDIT, on_click=lambda e, tile=list_tile, s_name=service_name, p_name=prop_name,  is_secure=False: save_data(e, tile, s_name, p_name, is_secure) if not tile.title.disabled else change_edit_mode(e, tile))                                                       
                        content_container.controls.append(list_tile)

                    exp = ft.ExpansionPanel(
                        bgcolor=ft.colors.BLUE_50,
                        header=ft.ListTile(title=ft.Text(title)),
                        content=content_container, 
                    )
                    panel.controls.append(exp)
            scrollable_container.controls.append(panel)
            page.add(scrollable_container)

        load_system_info()
        page.update()
