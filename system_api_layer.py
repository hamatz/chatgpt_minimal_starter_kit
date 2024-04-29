from system_file_controller import SystemFileController
from my_key_manager import MyKeyManager 

class SystemAPI:
    def __init__(self, key_manager: MyKeyManager, sys_file_ctrl: SystemFileController):
        self.__key_manager = key_manager
        self.__sys_file_ctrl = sys_file_ctrl

    def get_system_dicts_all(self) -> dict:
        """システム設定データの辞書を取得します。"""
        return self.__sys_file_ctrl.get_system_dicts_all()
    
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

    def save_system_dict(self, app_name: str, prop_name: str, data: dict) -> bool:
        """指定されたアプリケーション名とプロパティ名に辞書データを保存します。"""
        return self.__sys_file_ctrl.save_system_dict(app_name, prop_name, data)

    def load_system_dict(self, app_name: str, prop_name: str) -> dict:
        """指定されたアプリケーション名とプロパティ名から辞書データを読み込みます。"""
        data = self.__sys_file_ctrl.load_system_dict(app_name, prop_name)
        return data

    def delete_system_data(self, app_name: str, target_prop_name: str) -> bool:
        item = self.__sys_file_ctrl.delete_system_data(app_name, target_prop_name)
        return item if item is not True else False

    def encrypt_system_data(self, target: str) -> str:
        """指定されたテキストデータを暗号化します。"""
        return self.__key_manager.encrypt_data(target)

    def decrypt_system_data(self, target: str) -> str:
        """指定された暗号化されたテキストデータを復号化します。"""
        return self.__key_manager.decrypt_data(target)

    