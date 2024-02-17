import flet as ft

class UIComponentManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.components = {}

    def add_component(self, name, component):
        self.components[name] = component
        self.page.add(component)

    def get_component(self, name):
        return self.components.get(name)
