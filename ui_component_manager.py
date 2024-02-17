import flet as ft

class UIComponentManager:
    def __init__(self):
        self.components = {}

    def add_component(self, name, component):
        self.components[name] = component

    def get_component(self, name):
        return self.components.get(name)
