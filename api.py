import hashlib
from openai import AzureOpenAI, OpenAI

class API:

    def __init__(self, system_api):
        self.__system_api = system_api

    def get_chat_gpt_instance(self) -> OpenAI:
        openai_token_dict = self.__system_api.load_system_dict("System_Settings", "OpenAI_Token")
        my_openai_encrypted_token =openai_token_dict.get("api_key").get("value")
        my_openai_token = self.__system_api.decrypt_system_data(my_openai_encrypted_token)
        chat_client = OpenAI(api_key=my_openai_token,)
        return chat_client
    
    def get_openai_gpt_model_name(self) -> str:
        openai_model_dict = self.__system_api.load_system_dict("System_Settings", "GPT_model_name")
        my_openai_model_name =openai_model_dict.get("model_name").get("value")
        if not my_openai_model_name:
            my_openai_model_name = "gpt-4"
        return my_openai_model_name
    
    def get_azure_gpt_instance(self) -> AzureOpenAI:
        azure_token_dict = self.__system_api.load_system_dict("System_Settings", "Azure_Token")
        my_azure_encrypted_token =azure_token_dict.get("api_key").get("value")
        my_azure_token = self.__system_api.decrypt_system_data(my_azure_encrypted_token)
        azure_baseurl_dict = self.__system_api.load_system_dict("System_Settings", "Azure_base_url")
        my_azure_encrypted_baseurl =azure_baseurl_dict.get("api_base_url").get("value")
        my_azure_baseurl = self.__system_api.decrypt_system_data(my_azure_encrypted_baseurl)
        azure_api_version_dict = self.__system_api.load_system_dict("System_Settings", "Azure_API_Version")
        azure_api_version =azure_api_version_dict.get("api_version").get("value")

        chat_client = AzureOpenAI(azure_endpoint=my_azure_baseurl,
                api_version=azure_api_version,
                api_key=my_azure_token,
        )
        return chat_client
    
    def get_my_azure_deployment_name(self) -> str:
        azure_deployment_dict = self.__system_api.load_system_dict("System_Settings", "Azure_Deployment_name")
        my_azure_deployment_name =azure_deployment_dict.get("deployment_name").get("value")
        return my_azure_deployment_name
    
    def save_my_content_key(self, app_instance, content_key:str, caller_app_dir:str) -> bool:
        app_class_name = app_instance.__class__.__name__
        target_app_name = app_class_name + caller_app_dir
        target_app_hashed_name = hashlib.sha256(target_app_name.encode()).hexdigest()
        encryoted_key_data = self.__system_api.encrypt_system_data(content_key)
        encrypted_app_path = self.__system_api.encrypt_system_data(caller_app_dir)
        key_data_dict = {'value' : encryoted_key_data,
                         'app_dir' : encrypted_app_path}
        return self.__system_api.save_system_dict(target_app_hashed_name, "content_key",  key_data_dict)
    
    def load_my_content_key(self, app_instance, caller_app_dir:str) -> str:
        app_class_name = app_instance.__class__.__name__
        target_app_name = app_class_name + caller_app_dir
        target_app_hashed_name = hashlib.sha256(target_app_name.encode()).hexdigest()
        encrypted_my_key = self.__system_api.load_system_dict(target_app_hashed_name, "content_key").get("value")
        encrypted_caller_app_path = self.__system_api.load_system_dict(target_app_hashed_name, "content_key").get("app_dir")
        caller_app_path = self.__system_api.decrypt_system_data(encrypted_caller_app_path)
        if caller_app_path == caller_app_dir:
            return self.__system_api.decrypt_system_data(encrypted_my_key)
        else:
            return "Auth Error"
