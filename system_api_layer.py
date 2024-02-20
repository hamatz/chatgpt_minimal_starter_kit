from system_file_controller import SystemFileController
from my_key_manager import MyKeyManager 

class SystemAPI:

    def __init__(self, key_manager: MyKeyManager ,sys_file_ctrl: SystemFileController ):
        self.__key_manager = key_manager
        self.__sys_file_ctrl = sys_file_ctrl

    def save_system_text_data(self, app_name: str, prop_name: str, text: str) -> bool:
        return self.__sys_file_ctrl.save_text_data(app_name, prop_name, text) 

    def load_system_text_data(self, app_name: str, prop_name: str) -> str:
        return self.__sys_file_ctrl.load_text_data(app_name, prop_name) 
    
    def encrypt_system_data(self, target: str) -> str:
        return self.__key_manager.encrypt_data(target)
    
    def decrypt_system_data(self, target: str) -> str:
        return self.__key_manager.decrypt_data(target)
    