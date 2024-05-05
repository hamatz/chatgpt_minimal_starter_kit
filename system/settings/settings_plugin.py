import base64
import json
import os
import re
import flet as ft
from interfaces.system_plugin_interface import SystemPluginInterface
from typing import Callable
from system_api_layer import SystemAPI
from intent_conductor import IntentConductor
from exceptions import ValidationError, DuplicateKeyError

class SettingsPlugin(SystemPluginInterface):

    _instance = None
    
    def __new__(cls, system_api : SystemAPI, intent_conductor: IntentConductor):
        if cls._instance is None:
            cls._instance = super(SettingsPlugin, cls).__new__(cls)
            cls._instance.system_api = system_api
            cls._instance.intent_conductor = intent_conductor
        return cls._instance

    def load(self, page: ft.Page, function_to_top_page : Callable[[],None], plugin_dir_path: str, api):
        MY_SYSTEM_NAME = "CraftForgeBase"
        MY_APP_NAME = "System_Settings"
        page.clean()

        def toggle_debug_mode(e):
            debug_mode = e.control.value
            self.system_api.debug.set_debug_mode(debug_mode)
            self.settings_info_dict = self.system_api.settings.get_system_dicts_all()
            page.update()

        def reset_page_setting_and_close():
            page.overlay.remove(self.bottom_sheet)
            page.floating_action_button = None
            function_to_top_page()

        def get_component(component_name, **kwargs):
            api.logger.info(f"Requesting component: {component_name}")
            target_component = {"component_name": component_name}
            response = self.intent_conductor.send_event("get_component", target_component, sender_plugin=self.__class__.__name__, target_plugin="UIComponentToolkit")
            if response:
                component_class = response
                api.logger.info(f"Received component: {component_name}")
                return component_class(**kwargs)
            else:
                api.logger.error(f"component cannot be found: {component_name}")

        icon_path = os.path.join(plugin_dir_path, "back_button.png")
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            app_icon = ft.Image(src_base64=encoded_string, width=30, height=30)
        clickable_icon = ft.GestureDetector(
            content=app_icon,
            on_tap= lambda _: reset_page_setting_and_close()
        )
        my_header_widget = get_component("SimpleHeader2", icon=clickable_icon, title_text=MY_APP_NAME, color="#20b2aa")
        page.add(my_header_widget)

        def add_new_setting(system_dict : dict, setting_name :str, element_name :str, element_value: str, description_value: str, is_encrypted: bool) -> bool:
            if not re.match(r'^\w+$', setting_name):
                raise ValidationError("キー名は英数字のみ使用できます。")
            if setting_name in system_dict:
                raise DuplicateKeyError("既に同じキー名が存在します。")
            new_setting = {
                "value": element_value,
                "ui_type": "text",
            }
            description = {
                "value": description_value,
                "ui_type": "description",
            }
            self.system_api.settings.save_system_dict(MY_APP_NAME, setting_name, {
                element_name: new_setting,
                "description": description,
                "is_encrypted": {"value": is_encrypted, "ui_type": "toggle"}
            })
            self.settings_info_dict = self.system_api.settings.get_system_dicts_all()
            return True

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
                target_data = self.system_api.crypto.encrypt_system_data(edited_data)
                tile.title.value = target_data  # UI上で暗号化された値を表示する必要があるかどうかは要検討。今のところは一度設定したら見えない方が安全なのでは？という方針
            else:
                target_data = edited_data
            ui_type = "description" if prop_name == "description" else "text"
            target_dict[prop_name] = {"value": target_data, "ui_type": ui_type}
            self.system_api.settings.save_system_dict(MY_APP_NAME, service_name, target_dict)
            self.settings_info_dict = self.system_api.settings.get_system_dicts_all()
            change_edit_mode(e, tile)  # 編集モードを切り替えて編集不可状態に戻す

        def load_system_info():
            system_data_dict = self.system_api.settings.get_system_dicts_all()
            self.settings_info_dict = system_data_dict.get(MY_APP_NAME, {})
            # settings_info_dictが空の場合、初期設定用のJSONデータを読み込む
            if not self.settings_info_dict:
                json_path = os.path.join(plugin_dir_path, 'initial_settings.json')
                with open(json_path, 'r', encoding='utf-8') as f:
                    initial_settings = json.load(f)
                    for service_name, settings in initial_settings.items():
                        title = service_name
                        setting_info = settings
                        self.system_api.settings.save_system_dict(MY_APP_NAME, service_name, setting_info)
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
            #debug_mode_toggle = ft.Switch(label="Debug Mode", value=self.system_api.debug.is_debug_mode(), on_change=toggle_debug_mode)
            debug_mode_toggle = get_component("CartoonSwitch", label="Debug Mode", value=self.system_api.debug.is_debug_mode(), on_change=toggle_debug_mode)
            debug_toggle_row = ft.Row(spacing=5, controls=[debug_mode_toggle], alignment=ft.MainAxisAlignment.END)
            page.add(debug_toggle_row)

            scrollable_container = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

            panel = ft.ExpansionPanelList(
                expand_icon_color=ft.colors.BLUE_GREY,
                elevation=8,
                divider_color=ft.colors.BLUE_GREY,
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

            def add_new_info(e):
                add_new_setting(self.settings_info_dict,tb1.value,tb2.value,tb3.value,tb4.value,tb5.value)
                bottom_sheet.open = False
                bottom_sheet.update()

            #tb1 = ft.TextField(label="設定情報名（英数字）")
            tb1 =  get_component("CartoonTextBox", label="設定情報名（英数字）")
            #tb2 = ft.TextField(label="設定情報要素名")
            tb2 =  get_component("CartoonTextBox", label="設定情報要素名")
            #tb3 = ft.TextField(label="設定情報の中身")
            tb3 =  get_component("CartoonTextBox", label="設定情報の中身")
            #tb4 = ft.TextField(label="説明文")
            tb4 =  get_component("CartoonTextBox", label="説明文")
            #tb5 = ft.Switch(label="暗号化要否", value=True, disabled=False)
            tb5 =  get_component("CartoonSwitch", label="暗号化要否", value=True, disabled=False)
            #b = ft.ElevatedButton(text="登録する", on_click=add_new_info)
            b = get_component("CartoonButton", text="登録する", icon=ft.icons.ADMIN_PANEL_SETTINGS,  on_click=add_new_info)

            def bs_dismissed(e):
                print("New Param was saved!")

            def show_edit_sheet(e):
                bottom_sheet.open = True
                bottom_sheet.update()

            bottom_sheet = ft.BottomSheet(
                ft.Container(
                    ft.Column(
                        [
                            ft.Column(
                                [
                                    tb1,tb2,tb3,tb4,tb5
                                ],
                            ),
                            ft.Column(
                                [
                                    b,
                                ],
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=10,
                    alignment=ft.alignment.center,
                ),
                open=False,
                on_dismiss=bs_dismissed,
            )
            page.overlay.append(bottom_sheet)
            self.bottom_sheet = bottom_sheet

            def fab_pressed(e):
                show_edit_sheet(e)

            page.floating_action_button = ft.FloatingActionButton(
                icon=ft.icons.ADD, on_click=fab_pressed, bgcolor=ft.colors.WHITE30,
            )

        load_system_info()
        page.update()