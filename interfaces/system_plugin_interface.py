import abc

class SystemPluginInterface(metaclass=abc.ABCMeta):
    def __init__(self, ui_manager, system_api, intent_conductor):
        self.ui_manager = ui_manager
        self.system_api = system_api
        self.intent_conductor = intent_conductor

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError("The load method must be implemented by the plugin.")