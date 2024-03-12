import ast
import os

class CodeSecurityScanner:
    @staticmethod
    def scan_for_forbidden_functions(folder_path):
        forbidden_code_found = False

        class ForbiddenFunctionFinder(ast.NodeVisitor):
            def __init__(self):
                # 特定のモジュールの関数名のみをチェックするため、モジュール名をキーとして関数名を値とする辞書を定義
                self.forbidden_functions = {
                    "os": ["system", "popen", "execl", "execle", "execlp", "execlpe", "execv", "execve", "execvp", "execvpe", "remove", "unlink", "rmdir", "removedirs", "rename"],
                }

            def visit_Call(self, node):
                # 関数呼び出しのノードがast.Attributeの場合、つまりモジュール名.関数名の形式の場合
                if isinstance(node.func, ast.Attribute):
                    module_name = getattr(node.func.value, 'id', None)  # モジュール名を取得
                    func_name = node.func.attr  # 関数名を取得
                    if module_name in self.forbidden_functions and func_name in self.forbidden_functions[module_name]:
                        # 禁止された関数が見つかった場合
                        print(f"Forbidden function call {module_name}.{func_name} found at line {node.lineno}")
                        return True  # または適切な処理を行う
                self.generic_visit(node)

        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".py"):  # Pythonのソースファイルのみを対象とする
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as source_file:
                            source_code = source_file.read()
                            if '\0' in source_code:
                                print(f"Warning: Null byte found in {file_path}. This file will be skipped.")
                                continue
                    except UnicodeDecodeError:
                        print(f"Warning: Unicode decode error in {file_path}. This file will be skipped.")
                        continue
                    tree = ast.parse(source_code, filename=file_path)
                    finder = ForbiddenFunctionFinder()
                    finder.visit(tree)
                    if forbidden_code_found:
                        return False
        # 悪意のあるコードが見つからなければ True を返す
        return True