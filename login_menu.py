from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen


# ========== ЭКРАН ВХОДА ==========
class LoginMenuScreen(MDScreen):
    """Главный экран"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "login_menu"
        self.md_bg_color = "white"

        main_layout = MDRelativeLayout()

        title = MDLabel(
            text="Pig Bank",
            halign="center",
            font_style="Display",
            theme_text_color="Custom",
            text_color="black",
            adaptive_height=True,
            pos_hint={"center_x": 0.5, "center_y": 0.6},
        )

        subtitle1 = MDLabel(
            text="Кофе",
            halign="center",
            font_style="Headline",
            role="small",
            theme_text_color="Custom",
            text_color="black",
            adaptive_height=True,
            pos_hint={"center_x": 0.5, "center_y": 0.55},
        )

        subtitle2 = MDLabel(
            text="Нажмите, чтобы открыть смену",
            halign="center",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            adaptive_height=True,
            pos_hint={"center_x": 0.5, "center_y": 0.45},
        )

        open_button = MDButton(
            MDButtonText(text="Открыть", theme_text_color="Custom", text_color="black"),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color="pink",
            pos_hint={"center_x": 0.5, "center_y": 0.38},
        )
        open_button.bind(on_release=self.go_to_barista_menu)

        main_layout.add_widget(title)
        main_layout.add_widget(subtitle1)
        main_layout.add_widget(subtitle2)
        main_layout.add_widget(open_button)

        self.add_widget(main_layout)

    def go_to_barista_menu(self, *args):
        self.manager.current = "barista_menu"
