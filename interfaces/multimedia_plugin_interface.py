from .plugin_interface import PluginInterface

class MultimediaPluginInterface(PluginInterface):
    def __init__(self, intent_conductor, api):
        super().__init__(intent_conductor, api)

    def record_audio(self, fs=16000):
        return self.api.multimedia.record_audio(fs=fs, caller_plugin=self.__class__.__name__)

    def play_audio(self, audio_segment):
        self.api.multimedia.play_audio(audio_segment, caller_plugin=self.__class__.__name__)

    def save_audio(self, filename, audio, fs=16000):
        self.api.multimedia.save_audio(filename, audio, fs=fs, caller_plugin=self.__class__.__name__)

    def transcribe_audio(self, file_path):
        return self.api.multimedia.transcribe_audio(file_path, caller_plugin=self.__class__.__name__)

    def get_text_response(self, prompt):
        return self.api.multimedia.get_text_response(prompt, caller_plugin=self.__class__.__name__)

    def text_to_speech(self, text):
        return self.api.multimedia.text_to_speech(text, caller_plugin=self.__class__.__name__)