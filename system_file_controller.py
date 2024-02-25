import json
import os

class SystemFileController:
    def __init__(self, system_filename: str, base_dir: str):
        system_file_path = os.path.join(base_dir, system_filename)
        self.system_filename = system_file_path
        if os.path.isfile(self.system_filename):
            with open(self.system_filename, 'r', encoding='utf-8') as f:
                self.my_system_file = json.load(f)
        else:
            self.my_system_file = {}

    def get_system_dicts_all(self) -> dict:
        return self.my_system_file.copy()

    def delete_system_data(self, app_name: str, target_prop_name: str) -> bool:
        items = self.my_system_file.get(app_name)
        if items and target_prop_name in items:
            del items[target_prop_name]
            self._save_to_file()
            return True
        return False

    def save_system_dict(self, app_name: str, prop_name: str, values: dict) -> bool:
        if app_name not in self.my_system_file:
            self.my_system_file[app_name] = {}
        self.my_system_file[app_name][prop_name] = values
        self._save_to_file()
        return True

    def load_system_dict(self, app_name: str, prop_name: str) -> dict:
        return self.my_system_file.get(app_name, {}).get(prop_name)

    def _save_to_file(self):
        with open(self.system_filename, 'w', encoding='utf-8') as f:
            json.dump(self.my_system_file, f, indent=4)