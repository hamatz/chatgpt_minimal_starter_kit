import abc

class PluginInterface(metaclass=abc.ABCMeta):
    def __init__(self, ui_manager):
        self.ui_manager = ui_manager

    @abc.abstractmethod
    def load(self):
        raise NotImplementedError("The load method must be implemented by the plugin.")