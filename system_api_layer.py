from system_file_controller import SystemFileController
from my_key_manager import MyKeyManager 

class SystemAPI:
    def __init__(self, key_manager: MyKeyManager, sys_file_ctrl: SystemFileController):
        self.__key_manager = key_manager
        self.__sys_file_ctrl = sys_file_ctrl
        self.settings = self.SettingsManager(self.__sys_file_ctrl)
        self.crypto = self.CryptoUtils(self.__key_manager)
        self.debug = self.DebugUtils(self.__sys_file_ctrl)

    class SettingsManager:
        def __init__(self, sys_file_ctrl: SystemFileController):
            self.__sys_file_ctrl = sys_file_ctrl

        def get_system_dicts_all(self) -> dict:
            """
            システム設定データの辞書を取得します。
            
            Returns:
                dict: システム設定データの辞書。
            """
            return self.__sys_file_ctrl.get_system_dicts_all()

        def save_system_dict(self, app_name: str, prop_name: str, data: dict) -> bool:
            """
            指定されたアプリケーション(プラグイン）名とプロパティ名に辞書データを保存します。
            
            Args:
                app_name (str): アプリケーション(プラグイン）名。
                prop_name (str): プロパティ名。
                data (dict): 保存する辞書データ。
            
            Returns:
                bool: 保存に成功した場合は True、失敗した場合は False。
            """
            return self.__sys_file_ctrl.save_system_dict(app_name, prop_name, data)

        def load_system_dict(self, app_name: str, prop_name: str) -> dict:
            """
            指定されたアプリケーション(プラグイン）名とプロパティ名から辞書データを読み込みます。
            
            Args:
                app_name (str): アプリケーション(プラグイン）名。
                prop_name (str): プロパティ名。
            
            Returns:
                dict: 読み込んだ辞書データ。
            """
            return self.__sys_file_ctrl.load_system_dict(app_name, prop_name)

        def delete_system_data(self, app_name: str, target_prop_name: str) -> bool:
            """
            指定されたアプリケーション(プラグイン）名とプロパティ名のデータを削除します。
            
            Args:
                app_name (str): アプリケーション(プラグイン）名。
                target_prop_name (str): 削除するプロパティ名。
            
            Returns:
                bool: 削除に成功した場合は True、失敗した場合は False。
            """
            return self.__sys_file_ctrl.delete_system_data(app_name, target_prop_name)

    class CryptoUtils:
        def __init__(self, key_manager: MyKeyManager):
            self.__key_manager = key_manager

        def encrypt_system_data(self, target: str) -> str:
            """
            指定されたテキストデータを暗号化します。
            
            Args:
                target (str): 暗号化するテキストデータ。
            
            Returns:
                str: 暗号化されたテキストデータ。
            """
            return self.__key_manager.encrypt_data(target)

        def decrypt_system_data(self, target: str) -> str:
            """
            指定された暗号化されたテキストデータを復号化します。
            
            Args:
                target (str): 復号する暗号化されたテキストデータ。
            
            Returns:
                str: 復号されたテキストデータ。
            """
            return self.__key_manager.decrypt_data(target)

    class DebugUtils:
        def __init__(self, sys_file_ctrl: SystemFileController):
            self.__sys_file_ctrl = sys_file_ctrl

        def set_debug_mode(self, debug_mode: bool) -> None:
            """
            デバッグモードを設定します。
            
            Args:
                debug_mode (bool): デバッグモードを有効にする場合は True、無効にする場合は False。
            """
            self.__sys_file_ctrl.save_system_dict("CraftForgeBase", "debug_mode", {"value": debug_mode})

        def is_debug_mode(self) -> bool:
            """
            現在のデバッグモードの状態を取得します。
            
            Returns:
                bool: デバッグモードが有効な場合は True、無効な場合は False。
            """
            debug_mode = self.__sys_file_ctrl.load_system_dict("CraftForgeBase", "debug_mode")
            if debug_mode is None:
                return False
            return debug_mode.get("value", False)