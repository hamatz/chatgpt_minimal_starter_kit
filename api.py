import hashlib
import os
import logging
from openai import AzureOpenAI, OpenAI
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain_community.chat_models.azure_openai import AzureChatOpenAI
from PyPDF2 import PdfReader

class API:

    def __init__(self, system_api):
        self.__system_api = system_api
        self.logger = self.Logger(system_api)
        self.content_km = self.ContentKeyManager(system_api)
        self.ai = self.AIUtils(system_api)
        self.files = self.FileUtils(system_api)

    def is_debug_mode(self) -> bool:
        """
        現在のデバッグモードの状態を取得します。
        
        Returns:
            bool: デバッグモードが有効な場合は True、無効な場合は False。
        """
        return self.__system_api.debug.is_debug_mode()
    
    class Logger:
        def __init__(self, system_api):
            self.__system_api = system_api
            self.__logger = logging.getLogger("CraftForge")
            self.__logger.setLevel(logging.DEBUG)

            # ログファイルへの出力設定
            log_file_path = "craftforge.log"  # ログファイルのパス
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.DEBUG)

            # コンソールへの出力設定
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # ログフォーマットの設定
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            # ロガーにハンドラを追加
            self.__logger.addHandler(file_handler)
            self.__logger.addHandler(console_handler)

        def debug(self, message):
            if self.__system_api.debug.is_debug_mode():
                self.__logger.debug(message)

        def info(self, message):
            if self.__system_api.debug.is_debug_mode():
                self.__logger.info(message)

        def warning(self, message):
            if self.__system_api.debug.is_debug_mode():
                self.__logger.warning(message)

        def error(self, message):
            if self.__system_api.debug.is_debug_mode():
                self.__logger.error(message)

    class ContentKeyManager:
        def __init__(self, system_api):
            self.__system_api = system_api

        def save_my_content_key(self, app_instance, content_key:str, caller_app_dir:str) -> bool:
            app_class_name = app_instance.__class__.__name__
            target_app_name = app_class_name + caller_app_dir
            target_app_hashed_name = hashlib.sha256(target_app_name.encode()).hexdigest()
            encryoted_key_data = self.__system_api.crypto.encrypt_system_data(content_key)
            encrypted_app_path = self.__system_api.crypto.encrypt_system_data(caller_app_dir)
            key_data_dict = {'value' : encryoted_key_data,
                             'app_dir' : encrypted_app_path}
            return self.__system_api.settings.save_system_dict(target_app_hashed_name, "content_key",  key_data_dict)

        def load_my_content_key(self, app_instance, caller_app_dir:str) -> str:
            app_class_name = app_instance.__class__.__name__
            target_app_name = app_class_name + caller_app_dir
            target_app_hashed_name = hashlib.sha256(target_app_name.encode()).hexdigest()
            encrypted_my_key = self.__system_api.settings.load_system_dict(target_app_hashed_name, "content_key").get("value")
            encrypted_caller_app_path = self.__system_api.settings.load_system_dict(target_app_hashed_name, "content_key").get("app_dir")
            caller_app_path = self.__system_api.crypto.decrypt_system_data(encrypted_caller_app_path)
            if caller_app_path == caller_app_dir:
                return self.__system_api.crypto.decrypt_system_data(encrypted_my_key)
            else:
                return "Auth Error"

    class AIUtils:
        def __init__(self, system_api):
            self.__system_api = system_api

        def get_chat_gpt_instance(self) -> OpenAI:
            openai_token_dict = self.__system_api.settings.load_system_dict("System_Settings", "OpenAI_Token")
            my_openai_encrypted_token =openai_token_dict.get("api_key").get("value")
            my_openai_token = self.__system_api.crypto.decrypt_system_data(my_openai_encrypted_token)
            chat_client = OpenAI(api_key=my_openai_token,)
            return chat_client

        def get_openai_gpt_model_name(self) -> str:
            openai_model_dict = self.__system_api.settings.load_system_dict("System_Settings", "GPT_model_name")
            my_openai_model_name =openai_model_dict.get("model_name").get("value")
            if not my_openai_model_name:
                my_openai_model_name = "gpt-4"
            return my_openai_model_name

        def get_azure_gpt_instance(self) -> AzureOpenAI:
            azure_token_dict = self.__system_api.settings.load_system_dict("System_Settings", "Azure_Token")
            my_azure_encrypted_token =azure_token_dict.get("api_key").get("value")
            my_azure_token = self.__system_api.crypto.decrypt_system_data(my_azure_encrypted_token)
            azure_baseurl_dict = self.__system_api.settings.load_system_dict("System_Settings", "Azure_base_url")
            my_azure_encrypted_baseurl =azure_baseurl_dict.get("api_base_url").get("value")
            my_azure_baseurl = self.__system_api.crypto.decrypt_system_data(my_azure_encrypted_baseurl)
            azure_api_version_dict = self.__system_api.settings.load_system_dict("System_Settings", "Azure_API_Version")
            azure_api_version =azure_api_version_dict.get("api_version").get("value")

            chat_client = AzureOpenAI(azure_endpoint=my_azure_baseurl,
                    api_version=azure_api_version,
                    api_key=my_azure_token,
            )
            return chat_client

        def get_azure_chat_openai_instance(self, temperature) -> AzureChatOpenAI:
            azure_token_dict = self.__system_api.settings.load_system_dict("System_Settings", "Azure_Token")
            my_azure_encrypted_token =azure_token_dict.get("api_key").get("value")
            my_azure_token = self.__system_api.crypto.decrypt_system_data(my_azure_encrypted_token)
            azure_baseurl_dict = self.__system_api.settings.load_system_dict("System_Settings", "Azure_base_url")
            my_azure_encrypted_baseurl =azure_baseurl_dict.get("api_base_url").get("value")
            my_azure_baseurl = self.__system_api.crypto.decrypt_system_data(my_azure_encrypted_baseurl)
            azure_api_version_dict = self.__system_api.settings.load_system_dict("System_Settings", "Azure_API_Version")
            azure_api_version =azure_api_version_dict.get("api_version").get("value")
            azure_deployment_dict = self.__system_api.settings.load_system_dict("System_Settings", "Azure_Deployment_name")
            my_azure_deployment_name =azure_deployment_dict.get("deployment_name").get("value")
            azure_chat_openai_client = AzureChatOpenAI(azure_endpoint=my_azure_baseurl,
                    openai_api_version=azure_api_version,
                    deployment_name=my_azure_deployment_name,
                    openai_api_key=my_azure_token,
                    temperature = temperature,
                    streaming=True)
            return azure_chat_openai_client

        def get_my_azure_deployment_name(self) -> str:
            azure_deployment_dict = self.__system_api.settings.load_system_dict("System_Settings", "Azure_Deployment_name")
            my_azure_deployment_name =azure_deployment_dict.get("deployment_name").get("value")
            return my_azure_deployment_name

        def load_qdrant_for_azure(self, app_path : str, qdrant_path : str, collection_name : str, vector_param_size : int, vector_param_distance : Distance):
            my_qdrant_path = os.path.join(app_path,qdrant_path)
            if not os.path.exists(my_qdrant_path):
                os.makedirs(my_qdrant_path)
            client = QdrantClient(path= my_qdrant_path)
            collections = client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            if collection_name not in collection_names:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_param_size, distance=vector_param_distance),
                )
                self.__system_api.logger.info('collection created')
            azure_token_dict = self.__system_api.settings.load_system_dict("System_Settings", "Azure_Token")
            my_azure_encrypted_token =azure_token_dict.get("api_key").get("value")
            my_azure_token = self.__system_api.crypto.decrypt_system_data(my_azure_encrypted_token)
            azure_baseurl_dict = self.__system_api.settings.load_system_dict("System_Settings", "Azure_base_url")
            my_azure_encrypted_baseurl =azure_baseurl_dict.get("api_base_url").get("value")
            my_azure_baseurl = self.__system_api.crypto.decrypt_system_data(my_azure_encrypted_baseurl)
            azure_api_version_dict = self.__system_api.settings.load_system_dict("System_Settings", "Azure_API_Version")
            azure_api_version =azure_api_version_dict.get("api_version").get("value")
            azure_embeddings_deployment_dict = self.__system_api.settings.load_system_dict("System_Settings", "Azure_Embeddings_Deployment_name")
            my_azure_embeddings_deployment_name =azure_embeddings_deployment_dict.get("deployment_name").get("value")
            return Qdrant(
                client=client,
                collection_name=collection_name, 
                embeddings=AzureOpenAIEmbeddings(openai_api_type="azure", api_key=my_azure_token, base_url=my_azure_baseurl, api_version=azure_api_version, deployment=my_azure_embeddings_deployment_name)
            )

    class FileUtils:
        def __init__(self, system_api):
            self.__system_api = system_api

        def get_pdf_reader(self, target_file) -> PdfReader:
            return PdfReader(target_file)

        def getSharedFolderPath(self, folder_name: str, owner_plugin: str, accessing_plugin: str) -> str:
            shared_folders = self.__system_api.settings.load_system_dict("SharedFolderManager", owner_plugin)
            if shared_folders and folder_name in shared_folders:
                folder_info = shared_folders[folder_name]
                permissions = folder_info["permissions"]
                if accessing_plugin in permissions:
                    # アクセス権限を確認
                    folder_data = permissions[accessing_plugin]
                    folder_path = folder_data["path"]
                    permission = folder_data["permission"]
                    if permission in ["read", "write", "execute"]:
                        return folder_path
            raise PermissionError("Access denied.")


