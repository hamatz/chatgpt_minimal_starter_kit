import abc

class SystemPluginInterface(metaclass=abc.ABCMeta):
    def __init__(self, system_api, intent_conductor, api):
        self.system_api = system_api
        self.intent_conductor = intent_conductor
        self.api = api

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError("The load method must be implemented by the plugin.")