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
            return self.__sys_file_ctrl.get_system_dicts_all()

        def save_system_dict(self, app_name: str, prop_name: str, data: dict) -> bool:
            return self.__sys_file_ctrl.save_system_dict(app_name, prop_name, data)

        def load_system_dict(self, app_name: str, prop_name: str) -> dict:
            return self.__sys_file_ctrl.load_system_dict(app_name, prop_name)

        def delete_system_data(self, app_name: str, target_prop_name: str) -> bool:
            return self.__sys_file_ctrl.delete_system_data(app_name, target_prop_name)

    class CryptoUtils:
        def __init__(self, key_manager: MyKeyManager):
            self.__key_manager = key_manager

        def encrypt_system_data(self, target: str) -> str:
            return self.__key_manager.encrypt_data(target)

        def decrypt_system_data(self, target: str) -> str:
            return self.__key_manager.decrypt_data(target)

    class DebugUtils:
        def __init__(self, sys_file_ctrl: SystemFileController):
            self.__sys_file_ctrl = sys_file_ctrl

        def set_debug_mode(self, debug_mode: bool) -> None:
            self.__sys_file_ctrl.save_system_dict("CraftForgeBase", "debug_mode", {"value": debug_mode})

        def is_debug_mode(self) -> bool:
            debug_mode = self.__sys_file_ctrl.load_system_dict("CraftForgeBase", "debug_mode")
            if debug_mode is None:
                return False
            return debug_mode.get("value", False) 