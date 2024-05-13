import base64
import os
import flet as ft
from interfaces.plugin_interface import PluginInterface

class AIKaigiPlugin(PluginInterface):
    _instance = None
    
    def __new__(cls, intent_conductor, api):
        if cls._instance is None:
            cls._instance = super(AIKaigiPlugin, cls).__new__(cls)
            cls._instance.intent_conductor = intent_conductor
            cls._instance.api = api
            cls._instance.api_type = "OpenAI"
        return cls._instance

    def load(self, page: ft.Page, function_to_top_page, my_app_path: str, loaded_callback):
        def get_component(component_name, **kwargs):
            self.api.logger.info(f"Requesting component: {component_name}")
            target_component = {"component_name": component_name}
            response = self.intent_conductor.send_event("get_component", target_component, sender_plugin=self.__class__.__name__, target_plugin="UIComponentToolkit")
            if response:
                component_class = response
                self.api.logger.info(f"Received component: {component_name}")
                return component_class(**kwargs)
            else:
                self.api.logger.error(f"component cannot be found: {component_name}")

        def api_type_selected(e):
            self.api_type = api_type_dropdown.value
            page.update()

        def run_chat_flow(e):
            run_button.disabled = True
            spinner.visible = True
            page.update()

            template_dir = os.path.join(my_app_path, "templates")
            prompt_templates = []
            for i in range(1, 4):
                template_file = os.path.join(template_dir, f"template{i}.md")
                with open(template_file, "r") as f:
                    prompt_templates.append(f.read())

            def send_chat_request(prompt):
                response = self.intent_conductor.send_event(
                    "chat_request",
                    {"prompt": prompt, "api_type": self.api_type}, 
                    sender_plugin=self.__class__.__name__,
                    target_plugin="SampleChat"
                )
                return response

            question = question_textbox.get_value()
            response1 = send_chat_request(prompt_templates[0].format(question=question))
            chat_result.controls.append(ft.Text(f"{response1}"))
            page.update()

            response2 = send_chat_request(prompt_templates[1].format(question=question, prev_response=response1))
            chat_result.controls.append(ft.Text(f"{response2}"))
            page.update()

            response3 = send_chat_request(prompt_templates[2].format(question=question, prev_response=response2))
            chat_result.controls.append(ft.Text(f"{response3}"))
            page.update()

            run_button.disabled = False
            spinner.visible = False
            page.update()

        icon_path = os.path.join(my_app_path, "back_button.png")
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            app_icon = ft.Image(src_base64=encoded_string, width=30, height=30)
        clickable_icon = ft.GestureDetector(
            content=app_icon,
            on_tap= lambda _: function_to_top_page()
        )
        my_header_widget = get_component("SimpleHeader2", icon=clickable_icon, title_text= "エーアイKaigi v.0.1.0", color="#20b2aa")
        api_type_dropdown = get_component("CartoonDropdown", options=["OpenAI", "Azure"], value=self.api_type, on_change=api_type_selected)
        button_container = ft.Row(spacing=5, controls=[api_type_dropdown], alignment=ft.MainAxisAlignment.END)
        question_textbox = get_component("CartoonTextBox", label="質問を入力してください")
        run_button = get_component("CartoonButton", text="実行", on_click=run_chat_flow)
        spinner = ft.ProgressRing(visible=False, color="blue", stroke_width=2)
        chat_result = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)

        loaded_callback()
        page.clean()
        page.add(my_header_widget)
        page.add(button_container)
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("お題に対してAI達のディスカッションを眺めるプラグインです。お題となる質問を入力し、AI達にディスカッションをしてもらいましょう"),
                        question_textbox,
                        ft.Row(
                            [
                                run_button,
                                spinner,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        chat_result,
                    ],
                    spacing=20,
                ),
                padding=30,
                expand=True,
            )
        )
        page.update()