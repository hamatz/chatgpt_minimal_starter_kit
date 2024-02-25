import flet as ft

class ChatMessage(ft.Row):
    def __init__(self, user_name: str, message: str, page: ft.Page):
        super().__init__()
        text_size = page.window_width - 150
        self.vertical_alignment="start"
        # self.messege_area = ft.Markdown(message, selectable=True,expand=True, 
        #                     extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        #                     on_tap_link=lambda e: page.launch_url(e.data),)
        self.messege_area = ft.Text(message, selectable=True, width=text_size) 
        self.controls= [
                ft.CircleAvatar(
                    content=ft.Text(self.get_initials(user_name)),
                    color=ft.colors.WHITE,
                    bgcolor=self.get_avatar_color(user_name),
                ),
                ft.Column(
                    [
                        ft.Text(user_name, weight="bold"),
                        self.messege_area,
                    ],
                    tight=True,
                    spacing=5,
                ),]

    def set_message(self, messsage: str):
        self.messege_area.value = messsage

    def get_initials(self, user_name: str):
        if user_name:
            return user_name[:1].capitalize()
        else:
            return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]