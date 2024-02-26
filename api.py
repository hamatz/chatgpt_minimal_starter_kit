from openai import AzureOpenAI, OpenAI

class API:

    def __init__(self, system_api):
        self.__system_api = system_api

    def get_chat_gpt_instance(self):
        openai_token_dict = self.__system_api.load_system_dict("System_Settings", "OpenAI_Token")
        my_openai_encrypted_token =openai_token_dict.get("api_key").get("value")
        my_openai_token = self.__system_api.decrypt_system_data(my_openai_encrypted_token)
        chat_client = OpenAI(api_key=my_openai_token,)
        return chat_client
    
    def get_openai_gpt_model_name(self) -> str:
        openai_model_dict = self.__system_api.load_system_dict("System_Settings", "GPT_model_name")
        my_openai_model_name =openai_model_dict.get("model_name").get("value", "gpt-4")
        return my_openai_model_name
    
    def get_azure_gpt_instance(self):
        azure_token_dict = self.__system_api.load_system_dict("System_Settings", "Azure_Token")
        my_azure_encrypted_token =azure_token_dict.get("api_key").get("value")
        my_azure_token = self.__system_api.decrypt_system_data(my_azure_encrypted_token)
        azure_baseurl_dict = self.__system_api.load_system_dict("System_Settings", "Azure_base_url")
        my_azure_encrypted_baseurl =azure_baseurl_dict.get("api_base_url").get("value")
        my_azure_baseurl = self.__system_api.decrypt_system_data(my_azure_encrypted_baseurl)
        azure_api_version_dict = self.__system_api.load_system_dict("System_Settings", "Azure_base_url")
        azure_api_version =azure_api_version_dict.get("api_version").get("value")
        my_azure_baseurl = self.__system_api.decrypt_system_data(my_azure_encrypted_baseurl)

        chat_client = AzureOpenAI(azure_endpoint=my_azure_baseurl,
                api_version=azure_api_version,
                api_key=my_azure_token,
        )
        return chat_client


