import abc

class SystemPluginInterface(metaclass=abc.ABCMeta):
    def __init__(self, ui_manager, system_api):
        self.ui_manager = ui_manager
        self.system_api = system_api

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError("The load method must be implemented by the plugin.")