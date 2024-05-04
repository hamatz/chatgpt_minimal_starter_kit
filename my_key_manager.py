import base64
import hashlib
from datetime import datetime, timedelta
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flet.security import encrypt, decrypt
import os
import uuid
import json
import flet as ft
from ui_components.password_dialog import PasswordDialog

class MyKeyManager:

    def __init__(self, page: ft.Page, base_dir, my_key_file_name):
        self.__my_key_file_path = os.path.join(base_dir, my_key_file_name)
        self.__my_app_key = None
        self.__my_pass_phrase = None
        self.__page = page
        self.failed_attempts = 0
        self.locked_until = None

    def prompt_password_dialog(self):
        def close_dlg(e):
            self.__page.dialog.open = False
            self.__page.update()
            self.handle_key_file(password_input.value)

        def textbox_changed(e):
            password_input.value = e.control.value
            self.__page.update()

        password_input = ft.TextField(on_change=textbox_changed)
        dlg_modal = PasswordDialog("起動用パスワードの入力をお願いします", "Your Password", textbox_changed, "入力完了", close_dlg)
        self.__show_dialog(dlg_modal.build())

    def __show_dialog(self, dialog):
        self.__page.dialog = dialog
        self.__page.dialog.open = True
        self.__page.update()

    def __compute_hash(self, data) -> str:
        return hashlib.sha256(data).hexdigest()

    def __derive_key(self, password: bytes, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password)

    def __generate_my_key(self, user_input: str) -> None:
        password = user_input.encode()
        self.__my_pass_phrase = str(uuid.uuid4())

        salt = os.urandom(16) 
        my_key = self.__derive_key(password, salt)
        self.__my_app_key = my_key
        self.__save_my_key(salt)

    def __save_my_key(self, salt) -> None:
        # パスフレーズを暗号化
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(self.__my_app_key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        encrypted_pass_phrase = encryptor.update(self.__my_pass_phrase.encode()) + encryptor.finalize()
        content_key_hash = self.__compute_hash(self.__my_pass_phrase.encode())
        my_appkey_settings = {
            'salt': base64.b64encode(salt).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            "encrypted_content_key": base64.b64encode(encrypted_pass_phrase).decode('utf-8'),
            "content_key_hash": base64.b64encode(content_key_hash.encode()).decode('utf-8'), 
        }
        with open(self.__my_key_file_path, 'w') as f:
            json.dump(my_appkey_settings, f, indent=4)

    def load_my_key(self, password: str) -> bool:
        # ロックアウト状態のチェック
        if self.locked_until and self.locked_until > datetime.now():
            print("Account is locked.")
            self.__page.snack_bar = ft.SnackBar(ft.Text(f"システムロック中です {self.locked_until}"))
            self.__page.snack_bar.open = True
            self.__page.update()
            return False
        try:
            with open(self.__my_key_file_path, 'r') as f:
                key_data = json.load(f)
            salt = base64.b64decode(key_data['salt'])
            iv = base64.b64decode(key_data['iv'])
            encrypted_pass_phrase = base64.b64decode(key_data['encrypted_content_key'])
            content_key_hash = base64.b64decode(key_data['content_key_hash']).decode()
            derived_key = self.__derive_key(password.encode(), salt)
            # 復号
            cipher = Cipher(algorithms.AES(derived_key), modes.CFB(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_pass_phrase = decryptor.update(encrypted_pass_phrase) + decryptor.finalize()
            decrypted_pass_phrase_hash = hashlib.sha256(decrypted_pass_phrase).hexdigest() 
            if decrypted_pass_phrase_hash != content_key_hash:
                self.failed_attempts += 1
                self.__page.snack_bar = ft.SnackBar(ft.Text(f"パスワードエラーです {self.failed_attempts}/5"))
                self.__page.snack_bar.open = True
                self.__page.update()
                if self.failed_attempts >= 5:
                    # 5回失敗したら10分ロック
                    self.locked_until = datetime.now() + timedelta(minutes=10)
                return False
            # 成功したら試行回数をリセット
            self.failed_attempts = 0
            self.locked_until = None
            self.__my_app_key = derived_key
            self.__my_pass_phrase = decrypted_pass_phrase.decode()
            print("Key was successfully decrypted and loaded")
            return True
        except Exception as e:
            print(f"Failed to load key: {e}")
            return False

    def handle_key_file(self, password :str):
        if os.path.isfile(self.__my_key_file_path):
            # 鍵ファイルが存在する場合の処理
            if self.load_my_key(password):
                print("Key file successfully processed.")
            else:
                print("Failed to process key file.")
                self.prompt_password_dialog()
        else:
            # 鍵ファイルが存在しない場合の初期設定処理
            print("cannot find my_app_info.json")
            self.__generate_my_key(password)

    def encrypt_data(self, target: str) -> str:
        return encrypt(target, self.__my_pass_phrase)
    
    def decrypt_data(self, target: str) -> str:
        return decrypt(target, self.__my_pass_phrase)