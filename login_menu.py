from kivy.uix.image import Image
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen


class LoginMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "login_menu"
        self.md_bg_color = "white"

        logo = Image(
            source='assets/images/logo.png',
            size_hint=(None, None),
            size=("150dp", "150dp"),
            pos_hint={"center_x": 0.5},
        )

        title = MDLabel(
            text="PIG BANK",
            halign="center",
            valign="center",
            font_style="Display",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=40,
            pos_hint={"center_x": 0.5},
        )

        subtitle1 = MDLabel(
            text="Кофе, чай, свинки",
            halign="center",
            theme_text_color="Custom",
            text_color="black",
            adaptive_height=True,
            pos_hint={"center_x": 0.5},
        )

        subtitle2 = MDLabel(
            text="Нажмите, чтобы открыть смену",
            halign="center",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            adaptive_height=True,
            pos_hint={"center_x": 0.5},
        )

        open_button = MDButton(
            MDButtonIcon(icon="login", theme_text_color="Custom", text_color="black"),
            MDButtonText(text="Открыть", theme_text_color="Custom", text_color="black"),
            style="elevated",
            theme_bg_color="Custom",
            md_bg_color="pink",
            pos_hint={"center_x": 0.5},
            on_release=self.go_to_barista_menu
        )

        layout = MDBoxLayout(
            orientation="vertical",
            padding=5,
            spacing=5,
            pos_hint={"center_x": 0.5, "center_y": 0.7},
        )

        layout.add_widget(logo)
        layout.add_widget(MDBoxLayout(size_hint_y=None, height=40))

        layout.add_widget(title)

        layout.add_widget(subtitle1)
        layout.add_widget(MDBoxLayout(size_hint_y=None, height=40))

        layout.add_widget(subtitle2)
        layout.add_widget(open_button)

        main_layout = MDRelativeLayout()
        main_layout.add_widget(layout)

        self.add_widget(main_layout)

    def go_to_barista_menu(self, *args):
        self.manager.current = "barista_menu"
