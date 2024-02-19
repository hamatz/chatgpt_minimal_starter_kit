import json
import os

SYSTEM_FILENAME = "system_shared_data.json"

class SystemFileController:

    def __init__(self):
        is_key_file = os.path.isfile(SYSTEM_FILENAME)
        if is_key_file:
            with open(SYSTEM_FILENAME, 'rb') as f:
                    data = json.load(f)
                    self.my_system_file=data
        else:
            self.my_system_file={}

    def save_text_data(self, app_name: str, prop_name: str, text: str) -> bool:
        self.my_system_file[app_name] = {prop_name : text}
        with open(SYSTEM_FILENAME, 'w') as f:
            json.dump(self.my_system_file, f, indent=4)
            return True
    
    def load_text_data(self, app_name: str, prop_name: str) -> str:
         text = self.my_system_file[app_name][prop_name]
         if text:
            return text
         else:
            return None