import flet as ft

class TalkingCrystal(ft.UserControl):
    def __init__(self, name, recording_color, idle_color, on_click=None):
        super().__init__()
        self.name = name
        self.recording_color = recording_color
        self.idle_color = idle_color
        self.on_click = on_click
        self.is_recording = False
        self.crystal_size = 60
        self.crystal_border_radius = 30

    def build(self):
        self.crystal = ft.Container(
            width=self.crystal_size,
            height=self.crystal_size,
            bgcolor=self.idle_color,
            shape=ft.BoxShape.CIRCLE,
            border_radius=self.crystal_border_radius,
            alignment=ft.alignment.center,
        )

        self.spinner = ft.ProgressRing(
            width=30,
            height=30,
            color=ft.colors.WHITE,
            stroke_width=5,
            visible=False,
        )

        self.crystal_container = ft.Container(
            width=80,
            height=80,
            border_radius=50,
            ink=True,
            on_click=self.handle_click,
            content=ft.Stack([
                ft.Container(
                    self.crystal,
                    alignment=ft.alignment.center,
                ),
                ft.Container(
                    content=self.spinner,
                    alignment=ft.alignment.center,
                ),
            ]),
        )

        return self.crystal_container

    def handle_click(self, e):
        if self.on_click:
            self.on_click(e)
        self.toggle_recording(e)

    def toggle_recording(self, e):
        self.is_recording = not self.is_recording
        self.crystal.bgcolor = self.recording_color if self.is_recording else self.idle_color
        self.spinner.visible = self.is_recording
        self.crystal_container.update()