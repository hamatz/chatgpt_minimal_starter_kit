from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock, mock_open, patch
from my_key_manager import MyKeyManager
import flet as ft
import os

class TestMyKeyManager(unittest.TestCase):

    def setUp(self):
        self.page = MagicMock() 
        self.ui_manager = None
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.my_key_file_name = "test_my_key.json"
        self.key_manager = MyKeyManager(self.page, self.ui_manager, self.base_dir, self.my_key_file_name)

    @patch('builtins.print')
    def test_load_my_key_with_correct_password(self, mock_print):
        # 正しいパスワードでキーを生成し、保存
        correct_password = "correct_password"
        self.key_manager._MyKeyManager__generate_my_key(correct_password)
        # 正しいパスワードでキーをロードし、成功することを確認
        result = self.key_manager.load_my_key(correct_password)
        self.assertTrue(result)
        mock_print.assert_called_with("Key was successfully decrypted and loaded")

    @patch('builtins.print')
    def test_load_my_key_with_incorrect_password(self, mock_print):
        # 正しいパスワードでキーを生成し、保存
        correct_password = "correct_password"
        self.key_manager._MyKeyManager__generate_my_key(correct_password)
        # 誤ったパスワードでキーをロードし、失敗することを確認
        incorrect_password = "wrong_password"
        result = self.key_manager.load_my_key(incorrect_password)
        self.assertFalse(result)
        mock_print.assert_called_with('password error')

    @patch("hashlib.sha256")
    def test_compute_hash(self, mock_sha256):
        mock_sha256.return_value.hexdigest.return_value = "fake_hash"
        result = self.key_manager._MyKeyManager__compute_hash(b"data")
        self.assertEqual(result, "fake_hash")
        mock_sha256.assert_called_once_with(b"data")

    @patch("cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC.derive")
    def test_derive_key(self, mock_derive):
        mock_derive.return_value = b"derived_key"
        result = self.key_manager._MyKeyManager__derive_key(b"password", b"salt")
        self.assertEqual(result, b"derived_key")

    @patch('my_key_manager.datetime')
    def test_account_lockout(self, mock_datetime):
        # テスト開始時の時刻を設定
        start_time = datetime(2020, 1, 1)
        mock_datetime.now.return_value = start_time
        manager = MyKeyManager(MagicMock() , None, os.path.dirname(os.path.abspath(__file__)), "test_my_key.json")
        # 誤ったパスワードで5回ログインを試みる
        for _ in range(5):
            result = manager.load_my_key("wrong_password")
            self.assertFalse(result)  # ログインは失敗するはず
        # この時点でアカウントはロックされているはず
        self.assertIsNotNone(manager.locked_until)
        # ロックされた後の時刻をシミュレート
        mock_datetime.now.return_value = start_time + timedelta(minutes=11)
        # ロックが解除された後に正しいパスワードでログインを試みる
        correct_password = "correct_password"
        manager._MyKeyManager__generate_my_key(correct_password)
        result = manager.load_my_key(correct_password)
        # ログインが成功するはず
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()