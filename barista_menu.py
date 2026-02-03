from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialogButtonContainer, MDDialog, MDDialogHeadlineText, MDDialogSupportingText
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.widget import MDWidget

from headers import Barista, THIRD_COLOR


class BaristaMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "barista_menu"
        self.md_bg_color = "white"

        title = MDLabel(
            text="Укажите бариста",
            halign="center",
            theme_text_color="Custom",
            text_color="black",
            adaptive_height=True,
            pos_hint={"center_x": 0.5},
        )

        list_view = MDList(
            padding=10,
            spacing=15,
            size_hint=(0.6, 0.6),
            pos_hint={"center_x": 0.5},
        )

        for i, barista in enumerate(Barista.get_all_baristas()):
            item = MDCard(
                size_hint_y=None,
                height="50dp",
                style="elevated",
                theme_bg_color="Custom",
                md_bg_color=THIRD_COLOR,
                # theme_shadow_offset="Custom",
                # shadow_offset=(1, -2),
                # theme_shadow_softness="Custom",
                # shadow_softness=1,
                theme_elevation_level="Custom",
                elevation_level=1,
                on_release=lambda x, b=barista: self.select_barista(b),
            )

            barista_label = MDLabel(
                text=barista.name,
                theme_text_color="Custom",
                text_color="black",
                font_style="Title",
                role="small",
                halign="center",
                size_hint_x=0.9,
            )

            item.add_widget(barista_label)

            list_view.add_widget(item)

        layout = MDBoxLayout(
            orientation="vertical",
            padding=5,
            spacing=5,
            pos_hint={"center_x": 0.5, "center_y": 0.9},
        )

        layout.add_widget(title)
        layout.add_widget(list_view)

        back_button = MDButton(
            MDButtonIcon(icon="arrow-left", theme_text_color="Custom", text_color="black"),
            MDButtonText(text="Назад", theme_text_color="Custom", text_color="black"),
            style="elevated",
            theme_bg_color="Custom",
            md_bg_color="pink",
            pos_hint={"center_x": 0.5, "center_y": 0.1},
            on_release=self.go_back
        )

        main_layout = MDRelativeLayout()
        main_layout.add_widget(layout)
        main_layout.add_widget(back_button)

        self.add_widget(main_layout)

    def select_barista(self, barista: Barista):
        dialog = MDDialog(
            MDDialogHeadlineText(text="Открыть смену?", theme_text_color="Custom", text_color="black"),
            MDDialogSupportingText(text=f"Открыть смену для бариста {barista.name}?",
                                   theme_text_color="Custom", text_color="black"),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Отмена", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Да", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x, b=barista: self.confirm_open_shift(dialog, b)
                ),
            ),

            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def confirm_open_shift(self, dialog, barista: Barista):
        dialog.dismiss()

        app = MDApp.get_running_app()
        app.shift.open(barista)

        self.manager.current = "main_menu"
        cafe_screen = self.manager.get_screen("main_menu")
        cafe_screen.update_for_barista(app.shift.barista)

        MDSnackbar(
            MDSnackbarText(
                text=f"Смена открыта для бариста {barista.name}",
                theme_text_color="Custom",
                text_color="black"
            ),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
            theme_bg_color="Primary",
            radius=[10, 10, 10, 10],
            duration=1,
        ).open()

    def go_back(self, *args):
        self.manager.current = "login_menu"
