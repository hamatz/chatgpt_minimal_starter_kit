import base64
import os
import flet as ft
from interfaces.system_plugin_interface import SystemPluginInterface
from ui_component_manager import UIComponentManager
from system_api_layer import SystemAPI
import uuid

class SharedFolderManager(SystemPluginInterface):
    _instance = None

    def __new__(cls, ui_manager: UIComponentManager, system_api: SystemAPI):
        if cls._instance is None:
            cls._instance = super(SharedFolderManager, cls).__new__(cls)
            cls._instance.ui_manager = ui_manager
            cls._instance.system_api = system_api
        return cls._instance

    def load(self, page: ft.Page, function_to_top_page, plugin_dir_path: str, api):
        page.clean()

        self.page = page
        self.page_back_func = function_to_top_page
        self.plugin_dir = plugin_dir_path
        self.api = api

        def go_back_to_home(e):
            if hasattr(self, 'bottom_sheet') and self.bottom_sheet in self.page.overlay:
                self.page.overlay.remove(self.bottom_sheet)
            self.page.floating_action_button = None
            self.page_back_func()

        my_header_cmp = self.ui_manager.get_component("simple_header2")
        icon_path = os.path.join(plugin_dir_path, "back_button.png")
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            app_icon = ft.Image(src_base64=encoded_string, width=30, height=30)
        clickable_icon = ft.GestureDetector(
            content=app_icon,
            on_tap=lambda _: go_back_to_home(None)
        )
        my_header_instance = my_header_cmp(clickable_icon, "Shared Folder Manager", "#20b2aa")
        my_header_widget = my_header_instance.get_widget()
        page.add(my_header_widget)

        def manage_permissions_dlg(folder_id):
            folder_info = self.system_api.load_system_dict("SharedFolderManager", folder_id)
            folder_name = folder_info["name"]
            permissions = folder_info["permissions"]

            def grant_permission(e):
                permission = "write"
                self.grant_permission(folder_id, permission)
                bottom_sheet.open = False
                bottom_sheet.update()
                load_shared_folders()  # リストを更新
                page.update()  # ページを更新

            def revoke_permission(plugin_name):
                self.revoke_permission(folder_id, plugin_name)
                self.bottom_sheet.open = False
                self.bottom_sheet.update()
                self.page.update()
                self.load(self.page, self.page_back_func, self.plugin_dir, self.api)
            #事実上、何を選択してもフォルダパスを知った後は何でもできるので、現状は"write"で固定しておく
            permission_dropdown = ft.Dropdown(
                label="Permission",
                options=[
                    #ft.dropdown.Option("read"),
                    ft.dropdown.Option("write"),
                    #ft.dropdown.Option("execute"),
                ],
            )
            grant_button = ft.ElevatedButton(text="アクセス許可するプラグインを選択する", on_click=grant_permission)

            permissions_view = ft.Column([])
            for plugin_name, permission_data in permissions.items():
                list_tile = ft.ListTile(
                    title=ft.Text(plugin_name),
                    subtitle=ft.Text(permission_data["permission"]),
                    trailing=ft.IconButton(
                        icon=ft.icons.DELETE,
                        on_click=lambda _: revoke_permission(plugin_name),
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
                        tight=True,
                    ),
                    padding=10,
                ),
                open=True,
            )
            page.overlay.append(bottom_sheet)
            self.bottom_sheet = bottom_sheet
            page.update()

        def load_shared_folders():
            shared_folders = self.system_api.get_system_dicts_all().get("SharedFolderManager", {})

            scrollable_container = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

            panel = ft.ExpansionPanelList(
                expand_icon_color=ft.colors.AMBER,
                elevation=8,
                divider_color=ft.colors.AMBER,
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
                    bgcolor=ft.colors.BLUE_50,
                    header=ft.ListTile(
                        title=ft.Text(folder_name),
                        subtitle=ft.Text(f"Owner: {owner_plugin}"),
                        trailing=ft.IconButton(
                            icon=ft.icons.SETTINGS,
                            on_click=lambda _: manage_permissions_dlg(folder_id),
                        ),
                    ),
                    content=ft.Container(
                        content=content_container,
                        padding=10,
                    ),
                )
                panel.controls.append(exp)

            scrollable_container.controls.append(panel)
            page.add(scrollable_container)

        load_shared_folders()

        def create_new_folder_dlg(e):
            def create_folder(e):
                folder_name = new_folder_name.value
                owner_plugin = new_folder_owner.value
                folder_path = folder_picker.value
                if folder_name and owner_plugin and folder_path:
                    self.create_shared_folder(folder_name, owner_plugin, folder_path)
                    bottom_sheet.open = False
                    bottom_sheet.update()
                    page.clean()
                    load_shared_folders()  # リストを更新
                    page.update()  # ページを更新

            new_folder_name = ft.TextField(label="Folder Name")
            new_folder_owner = ft.TextField(label="Owner Plugin")
            folder_picker = ft.TextField(label="Folder Path", read_only=True, on_focus=lambda _: pick_folder())

            def pick_folder():
                dialog = ft.FilePicker(on_result=on_folder_selected)
                page.overlay.append(dialog)
                page.update()
                dialog.get_directory_path()

            def on_folder_selected(e: ft.FilePickerResultEvent):
                if e.path:
                    folder_picker.value = e.path
                    page.overlay.pop()
                    page.update()

            create_button = ft.ElevatedButton(text="Create", on_click=create_folder)

            bottom_sheet = ft.BottomSheet(
                ft.Container(
                    ft.Column(
                        [
                            new_folder_name,
                            new_folder_owner,
                            folder_picker,
                            create_button,
                        ],
                        tight=True,
                    ),
                    padding=10,
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
        self.system_api.save_system_dict("SharedFolderManager", folder_id, {
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
                folder_info = self.system_api.load_system_dict("SharedFolderManager", folder_id)
                folder_info["permissions"][plugin_name] = {"path": folder_path, "permission": permission}
                self.system_api.save_system_dict("SharedFolderManager", folder_id, folder_info)
                # ダイアログを閉じる
                self.page.dialog.open = False
                self.page.update()
                self.page.clean()
                self.load(self.page, self.page_back_func, self.plugin_dir,self.api)

        # ディレクトリ選択ダイアログを表示
        dialog = ft.FilePicker(on_result=on_directory_selected)
        self.page.dialog = dialog
        self.page.dialog.open = True
        self.page.update()
        dialog.get_directory_path()

    def revoke_permission(self, folder_id: str, plugin_name: str):
        # 共有フォルダのアクセス権限を取り消し
        folder_info = self.system_api.load_system_dict("SharedFolderManager", folder_id)
        folder_info["permissions"].pop(plugin_name, None)
        self.system_api.save_system_dict("SharedFolderManager", folder_id, folder_info)

    def access_shared_folder(self, folder_id: str, plugin_name: str) -> str:
        # 共有フォルダへのアクセス
        folder_info = self.system_api.load_system_dict("SharedFolderManager", folder_id)
        if plugin_name in folder_info["permissions"]:
            return folder_info["permissions"][plugin_name]
        else:
            raise PermissionError("Access denied.")