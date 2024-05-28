import abc

class PluginInterface(metaclass=abc.ABCMeta):
    def __init__(self, intent_conductor, api):
        self.intent_conductor = intent_conductor
        self.api = api

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError("The load method must be implemented by the plugin.")

    @classmethod
    def release_instance(cls):
        if hasattr(cls, '_instance'):
            cls._instance = None