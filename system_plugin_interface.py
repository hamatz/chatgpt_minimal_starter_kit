import abc

class SystemPluginInterface(metaclass=abc.ABCMeta):
    def __init__(self, ui_manager, system_key_manager):
        self.ui_manager = ui_manager
        self.system_key_manager = system_key_manager

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError("The load method must be implemented by the plugin.")