class ValidationError(Exception):
    """入力値がバリデーション条件を満たさない場合に発生する例外"""
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return f'Error occurred: {self.message}'

class DuplicateKeyError(Exception):
    """指定されたキーが既に存在する場合に発生する例外"""
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return f'Error occurred: {self.message}'