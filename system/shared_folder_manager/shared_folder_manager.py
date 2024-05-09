import base64
import os
import time
import flet as ft
from interfaces.system_plugin_interface import SystemPluginInterface
from system_api_layer import SystemAPI
from intent_conductor import IntentConductor
import uuid

class SharedFolderManager(SystemPluginInterface):
    _instance = None

    def __new__(cls, system_api: SystemAPI, intent_conductor: IntentConductor, api):
        if cls._instance is None:
            cls._instance = super(SharedFolderManager, cls).__new__(cls)
            cls._instance.system_api = system_api
            cls._instance.intent_conductor = intent_conductor
            cls._instance.api=api
        return cls._instance

    def load(self, page: ft.Page, function_to_top_page, plugin_dir_path: str):
        page.clean()

        self.page = page
        self.page_back_func = function_to_top_page
        self.plugin_dir = plugin_dir_path

        def go_back_to_home(e):
            if hasattr(self, 'bottom_sheet') and self.bottom_sheet in self.page.overlay:
                self.page.overlay.remove(self.bottom_sheet)
            self.page.floating_action_button = None
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
        my_header_widget = get_component("SimpleHeader2", icon=clickable_icon, title_text="共有フォルダ管理", color="#20b2aa")
        page.add(my_header_widget)

        def manage_permissions_dlg(folder_id):
            folder_info = self.system_api.settings.load_system_dict("SharedFolderManager", folder_id)
            folder_name = folder_info["name"]
            permissions = folder_info["permissions"]

            def grant_permission(e):
                permission = "write"
                self.grant_permission(folder_id, permission)
                bottom_sheet.open = False
                bottom_sheet.update()
                time.sleep(1)
                self.page.clean()
                self.load(self.page, self.page_back_func, self.plugin_dir)

            def revoke_permission(plugin_name):
                self.revoke_permission(folder_id, plugin_name)
                self.bottom_sheet.open = False
                self.bottom_sheet.update()
                time.sleep(1)
                self.page.clean()
                self.load(self.page, self.page_back_func, self.plugin_dir)
            #事実上、何を選択してもフォルダパスを知った後は何でもできるので、現状は"write"で固定しておく
            options = ["write"]
            permission_dropdown = get_component("CartoonDropdown", options=options, value="write", on_change=None)
            grant_button = get_component("CartoonButton", text="アクセス許可するプラグインを選択する",  on_click=grant_permission)

            permissions_view = ft.Column([])
            for plugin_name, permission_data in permissions.items():
                list_tile = ft.ListTile(
                    title=ft.Text(plugin_name),
                    subtitle=ft.Text(permission_data["permission"]),
                    trailing=ft.IconButton(
                        icon=ft.icons.DELETE,
                        on_click=lambda _, plugin=plugin_name: revoke_permission(plugin),
                    ),
                )
                permissions_view.controls.append(list_tile)

            bottom_sheet = ft.BottomSheet(
                ft.Container(
                    ft.Column(
                        [
                            ft.Text(f"Manage Permissions for: {folder_name}", weight=ft.FontWeight.BOLD),
                            permission_dropdown,
                            grant_button,
                            ft.Divider(),
                            permissions_view,
                        ],
                        #tight=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=10,
                ),
                open=True,
            )
            page.overlay.append(bottom_sheet)
            self.bottom_sheet = bottom_sheet
            page.update()

        def load_shared_folders():
            shared_folders = self.system_api.settings.get_system_dicts_all().get("SharedFolderManager", {})

            if not shared_folders:
                # 登録されているフォルダがない場合
                image_path = os.path.join(self.plugin_dir, "no_folders.png")
                try:
                    with open(image_path, "rb") as cover_image_file:
                        cover_encoded_string = base64.b64encode(cover_image_file.read()).decode("utf-8")
                    app_cover = ft.Image(src_base64=cover_encoded_string, width=300, height=300)
                except FileNotFoundError:
                    app_cover = ft.Text("画像が見つかりません", color=ft.colors.RED)

                message = ft.Text("共有したいフォルダを登録してください", size=20, color=ft.colors.BLUE_GREY_400)
                content = ft.Column(
                    [
                        app_cover,
                        message
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                )
            else:
                panel = ft.ExpansionPanelList(
                    expand_icon_color=ft.colors.BLUE_GREY,
                    elevation=8,
                    divider_color=ft.colors.BLUE_GREY,
                    controls=[],
                )

                for folder_id, folder_info in shared_folders.items():
                    folder_name = folder_info["name"]
                    owner_plugin = folder_info["owner"]
                    permissions = folder_info["permissions"]

                    content_container = ft.Column([])

                    for plugin_name, permission_data in permissions.items():
                        list_tile = ft.ListTile(
                            title=ft.Text(plugin_name),
                            subtitle=ft.Text(permission_data["permission"]),
                        )
                        content_container.controls.append(list_tile)

                    exp = ft.ExpansionPanel(
                        bgcolor=ft.colors.GREY_100,
                        header=ft.ListTile(
                            title=ft.Text(folder_name),
                            subtitle=ft.Text(f"Owner: {owner_plugin}"),
                            trailing=ft.IconButton(
                                icon=ft.icons.SETTINGS,
                                on_click=lambda _, fid=folder_id: manage_permissions_dlg(fid),
                            ),
                        ),
                        content=ft.Container(
                            content=content_container,
                            padding=10,
                        ),
                    )
                    panel.controls.append(exp)

                content = panel

            body_container = ft.Container(
                content=content,
                padding=ft.padding.only(top=20, left=50, right=50),
                alignment=ft.alignment.top_center,
                expand=True,
            )

            page.add(body_container)
            page.update()

        load_shared_folders()

        def create_new_folder_dlg(e):
            def create_folder(e):
                folder_name = new_folder_name.get_value()
                owner_plugin = new_folder_owner.get_value()
                folder_path = folder_picker.get_value()
                if folder_name and owner_plugin and folder_path:
                    self.create_shared_folder(folder_name, owner_plugin, folder_path)
                    bottom_sheet.open = False
                    bottom_sheet.update()
                    page.clean()
                    self.load(self.page, self.page_back_func, self.plugin_dir)

            new_folder_name = get_component("CartoonTextBox", label="Folder Name")
            new_folder_owner = get_component("CartoonTextBox", label="Owner Plugin")
            folder_picker = get_component("CartoonTextBox", label="Folder Path")

            def pick_folder(e):
                if e.path:
                    folder_picker.set_value(e.path)
                    page.update()

            def on_folder_picker_focus(e):
                dialog = ft.FilePicker(on_result=pick_folder)
                page.overlay.append(dialog)
                page.update()
                dialog.get_directory_path(dialog_title="フォルダを選択してください")

            folder_picker.on_focus = on_folder_picker_focus

            create_button = get_component("CartoonButton", text="登録する", icon=ft.icons.ADMIN_PANEL_SETTINGS,  on_click=create_folder)

            bottom_sheet = ft.BottomSheet(
                ft.Container(
                    ft.Column(
                        [
                            new_folder_name,
                            new_folder_owner,
                            folder_picker,
                            create_button,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=20,
                    alignment=ft.alignment.center,
                ),
                open=True,
            )
            page.overlay.append(bottom_sheet)
            self.bottom_sheet = bottom_sheet
            page.update()

        def fab_pressed(e):
            create_new_folder_dlg(e)

        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.icons.ADD, on_click=fab_pressed, bgcolor=ft.colors.WHITE30,
        )
        page.update()
        

    def create_shared_folder(self, folder_name: str, owner_plugin: str, folder_path: str) -> str:
        # 共有フォルダの作成
        folder_id = str(uuid.uuid4())
        # システム設定に共有フォルダの情報を保存
        self.system_api.settings.save_system_dict("SharedFolderManager", folder_id, {
            "name": folder_name,
            "owner": owner_plugin,
            "path": folder_path,
            "permissions": {}
        })
        return folder_id

    def grant_permission(self, folder_id: str, permission: str):
        def on_directory_selected(e: ft.FilePickerResultEvent):
            if e.path:
                folder_path = e.path
                # フォルダパスからプラグインのディレクトリ名を取得
                plugin_name = os.path.basename(folder_path)
                # 共有フォルダのアクセス権限を付与
                folder_info = self.system_api.settings.load_system_dict("SharedFolderManager", folder_id)
                folder_info["permissions"][plugin_name] = {"path": folder_path, "permission": permission}
                self.system_api.settings.save_system_dict("SharedFolderManager", folder_id, folder_info)
                # ダイアログを閉じる
                if dialog in self.page.overlay:
                    self.page.overlay.remove(dialog)
                self.page.update()
                self.page.clean()
                self.load(self.page, self.page_back_func, self.plugin_dir)

        # ディレクトリ選択ダイアログを表示
        dialog = ft.FilePicker(on_result=on_directory_selected)
        self.page.overlay.append(dialog)
        self.page.update()
        dialog.get_directory_path()

    def revoke_permission(self, folder_id: str, plugin_name: str):
        # 共有フォルダのアクセス権限を取り消し
        folder_info = self.system_api.settings.load_system_dict("SharedFolderManager", folder_id)
        folder_info["permissions"].pop(plugin_name, None)
        self.system_api.settings.save_system_dict("SharedFolderManager", folder_id, folder_info)

    def access_shared_folder(self, folder_id: str, plugin_name: str) -> str:
        # 共有フォルダへのアクセス
        folder_info = self.system_api.settings.load_system_dict("SharedFolderManager", folder_id)
        if plugin_name in folder_info["permissions"]:
            return folder_info["permissions"][plugin_name]
        else:
            raise PermissionError("Access denied.")