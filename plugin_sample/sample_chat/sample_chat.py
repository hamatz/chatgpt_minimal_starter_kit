import base64
import os
import flet as ft
from interfaces.plugin_interface import PluginInterface
from chat_message import ChatMessage
from api import API

class SampleChat(PluginInterface):
    _instance = None
    
    def __new__(cls, intent_conductor):
        if cls._instance is None:
            cls._instance = super(SampleChat, cls).__new__(cls)
            cls._instance.intent_conductor = intent_conductor
        return cls._instance

    def load(self, page: ft.Page, function_to_top_page, my_app_path: str, api):

        def get_answer(prompt, my_gpt_model):
            message=[{ "role": "user","content":prompt}]
            model_name = my_gpt_model if self.my_service == "OpenAI" else self.my_azure_deployment_name
            response = self.chat_client.chat.completions.create(
                model=model_name,
                messages=message,
                stream=True
            )
            return response
        
        def get_component(component_name, **kwargs):
            api.logger.info(f"Requesting component: {component_name}")
            target_component = {"component_name": component_name}
            response = self.intent_conductor.send_event("get_component", target_component, sender_plugin=self.__class__.__name__, target_plugin="UIComponentToolkit")
            if response:
                component_class = response
                api.logger.info(f"Received component: {component_name}")
                return component_class(**kwargs)
            else:
                api.logger.error(f"component cannot be found: {component_name}")
        
        page.clean()
        self.my_service = "OpenAI"

        def service_selected(e):
            self.my_service = dropdown.value
            set_gpt_client()
            page.update()

        icon_path = os.path.join(my_app_path, "back_button.png")
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            app_icon = ft.Image(src_base64=encoded_string, width=30, height=30)
        clickable_icon = ft.GestureDetector(
            content=app_icon,
            on_tap= lambda _: reset_page_setting_and_close()
        )
        my_header_widget = get_component("SimpleHeader2", icon=clickable_icon, title_text= "Sample Chat v.0.1.0", color="#20b2aa")
        
        page.add(my_header_widget)

        #button = ft.ElevatedButton(text="決定", on_click=service_selected)
        button = get_component("CartoonButton", text="決定", on_click=service_selected)
        dropdown = get_component("CartoonDropdown", options=["OpenAI", "Azure"], value=self.my_service, on_change=service_selected, bg_color=ft.colors.YELLOW_300, txt_color=ft.colors.BLACK)
        button_container = ft.Row(spacing=5, controls=[dropdown, button], alignment=ft.MainAxisAlignment.END)
        page.add(button_container)

        def set_gpt_client() -> None:
            if self.my_service == "OpenAI":
                self.chat_client = api.ai.get_chat_gpt_instance()
                self.my_gpt_model = api.ai.get_openai_gpt_model_name()
            elif self.my_service == "Azure":
                self.chat_client = api.ai.get_azure_gpt_instance()
                self.my_azure_deployment_name = api.ai.get_my_azure_deployment_name()

        def reset_page_setting_and_close():
            page.horizontal_alignment = ft.CrossAxisAlignment.START
            function_to_top_page()

        set_gpt_client()

        page.horizontal_alignment = "stretch"

        current_chat_area = None
        user_message = ""

        def textbox_changed(e):
            nonlocal current_chat_area
            nonlocal user_message
            user_message= e.control.value
            if current_chat_area == None:
                current_chat_area = ChatMessage("あなた", user_message, page)
                chat.controls.append(current_chat_area)
                page.update()
            else:
                current_chat_area.set_message(user_message)
                page.update()

        def send_message_click(e):
            nonlocal user_message
            nonlocal current_chat_area
            if new_message.value != "":
                new_message.value = ""
                reply_text = ""
                cm = ChatMessage("GPT君", reply_text, page)
                chat.controls.append(cm)
                answer = get_answer(user_message, self.my_gpt_model)
                for chunk in answer:
                    chunk_message = chunk.choices[0].delta.content
                    if chunk_message is not None:
                        reply_text += chunk_message
                        cm.set_message(reply_text)
                        page.update()
                new_message.focus()
                user_message = ""
                current_chat_area = None
                page.update()

        # Chat messages
        chat = ft.ListView(
            expand=True,
            width=500,
            spacing=10,
            auto_scroll=True,
            divider_thickness = 1
        )

        # A new message entry form
        new_message = ft.TextField(
            hint_text="ご質問をどうぞ！",
            autofocus=True,
            #shift_enter=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            expand=True,
            on_change=lambda e:textbox_changed(e),
            on_submit=send_message_click,
            border_color=ft.colors.BLACK,
            text_style=ft.TextStyle(color=ft.colors.BLACK),
            border_radius=ft.border_radius.all(30),
            bgcolor=ft.colors.WHITE,
        )

        # Add everything to the page
        send_button = get_component("CartoonButton", text="送信",  on_click=send_message_click)
        page.add(
            ft.Container(
                content=chat,
                border=ft.border.all(1, ft.colors.OUTLINE),
                border_radius=5,
                padding=10,
                expand=True,
            ),
            ft.Row(
                [
                    new_message,
                    send_button,
                    # ft.IconButton(
                    #     icon=ft.icons.SEND_ROUNDED,
                    #     tooltip="Send message",
                    #     on_click=send_message_click,
                    #     #icon_color=ft.colors.LIGHT_BLUE_400,
                    # ),
                ]
            ),
        )
        page.update()