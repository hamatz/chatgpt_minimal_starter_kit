import unittest
from unittest.mock import patch
from my_key_manager import MyKeyManager
import flet as ft
import os

class TestMyKeyManager(unittest.TestCase):

    def setUp(self):
        self.page = None
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
        mock_print.assert_called_with("Failed to load key: 'NoneType' object has no attribute 'snack_bar'")

if __name__ == '__main__':
    unittest.main()