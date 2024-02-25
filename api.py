from openai import OpenAI

class API:
    def __init__(self, system_api):
        self.__system_api = system_api

    def get_chat_gpt_instance(self):
        open_ai_token_dict = self.__system_api.load_system_dict("System_Settings", "OpenAI_Token")
        my_open_ai_encrypted_token =open_ai_token_dict.get("api_key").get("value")
        my_open_ai_token = self.__system_api.decrypt_system_data(my_open_ai_encrypted_token)
        chat_client = OpenAI(api_key=my_open_ai_token,)
        return chat_client

