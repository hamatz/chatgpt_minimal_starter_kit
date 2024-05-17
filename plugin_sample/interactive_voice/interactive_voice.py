import base64
import os
import time
import flet as ft
from flet import Image
from api import API
from intent_conductor import IntentConductor
from interfaces.multimedia_plugin_interface import MultimediaPluginInterface

class InteractiveVoicePlugin(MultimediaPluginInterface):
    _instance = None

    def __new__(cls, intent_conductor: IntentConductor, api: API):
        if cls._instance is None:
            cls._instance = super(InteractiveVoicePlugin, cls).__new__(cls)
            cls._instance.intent_conductor = intent_conductor
            cls._instance.api = api
        return cls._instance

    def load(self, page: ft.Page, function_to_top_page, plugin_dir_path: str, loaded_callback):
        self.page = page
        self.page_back_func = function_to_top_page
        self.plugin_dir = plugin_dir_path

        self.messages = [{"role": "system", "content": "You are a helpful assistant."}]

        def go_back_to_home(e):
            self.is_recording = False
            self.talking_crystal.is_recording = False
            self.talking_crystal.spinner.visible = False
            self.talking_crystal.crystal_container.update()
            self.page_back_func()

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

        def on_crystal_click(e):
            if not self.is_recording:
                self.start_recording()
            else:
                self.stop_recording()

        icon_path = os.path.join(plugin_dir_path, "back_button.png")
        with open(icon_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
            app_icon = ft.Image(src_base64=encoded_string, width=30, height=30)
        clickable_icon = ft.GestureDetector(
            content=app_icon,
            on_tap=lambda _: go_back_to_home(None)
        )
        my_header_widget = get_component("SimpleHeader2", icon=clickable_icon, title_text="Interactive Voice v.0.1.0", color="#20b2aa")
        self.talking_crystal = get_component("TalkingCrystal", name="Push to Talk", recording_color=ft.colors.RED, idle_color=ft.colors.BLUE_GREY_200,on_click=on_crystal_click)
        self.chat_view = ft.ListView(expand=1, spacing=10, auto_scroll=True)
        self.api.multimedia.pre_process(threshold=500, silence_duration=1, voice="nova")

        self.is_recording = False

        self.page.clean()
        self.page.add(my_header_widget)
        self.page.add(
            self.chat_view,
            ft.Container(
                content=self.talking_crystal,
                alignment=ft.alignment.center,
                padding=10,
            ),
        )
        loaded_callback()
        page.update()

    def start_recording(self):
        self.is_recording = True
        
        while self.is_recording:
            self.talking_crystal.is_recording = True
            self.talking_crystal.spinner.visible = True
            self.talking_crystal.crystal_container.update()
            
            self.chat_view.controls.append(ft.Text("Recording started..."))
            self.page.update()

            audio = self.record_audio(fs=16000)

            self.talking_crystal.is_recording = False
            self.talking_crystal.spinner.visible = False
            self.talking_crystal.crystal_container.update()

            self.save_audio("input.wav", audio)

            self.chat_view.controls.append(ft.Text("Recording finished."))
            self.page.update()

            transcribed_text = self.transcribe_audio("input.wav")
            self.chat_view.controls.append(ft.Text(f"Transcribed Text: {transcribed_text}"))
            self.page.update()

            self.messages.append({"role": "user", "content": transcribed_text})
            response_text = self.get_text_response(self.messages)
            self.chat_view.controls.append(ft.Text(f"Response Text: {response_text}"))
            self.messages.append({"role": "assistant", "content": response_text})
            self.page.update()

            saved_file_path = self.text_to_speech(response_text)
            self.play_audio(saved_file_path)

            # 一定時間待機してから次の録音を開始します
            self.page.update()
            time.sleep(1)

    def stop_recording(self):
        self.is_recording = False
        self.talking_crystal.is_recording = False
        self.talking_crystal.spinner.visible = False
        self.talking_crystal.crystal.bgcolor = self.talking_crystal.idle_color
        self.talking_crystal.crystal_container.update()