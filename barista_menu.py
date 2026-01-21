from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.dialog import MDDialogButtonContainer, MDDialog, MDDialogHeadlineText, MDDialogSupportingText
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItem, MDListItemHeadlineText, MDList
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.widget import MDWidget

from headers import Shift, Barista, BARISTAS, SECONDARY_COLOR, THIRD_COLOR


class BaristaMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "barista_menu"
        self.md_bg_color = "white"

        main_layout = MDBoxLayout(
            orientation="vertical",
            padding=15,
            spacing=15,
            size_hint=(0.8, 0.9),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        title = MDLabel(
            text="Укажите бариста",
            halign="center",
            font_style="Headline",
            role="small",
            theme_text_color="Custom",
            text_color="black",
            adaptive_height=True,
        )

        scroll_view = MDScrollView()
        list_view = MDList()

        for i, barista in enumerate(BARISTAS):
            bg_color = SECONDARY_COLOR if i % 2 == 0 else THIRD_COLOR

            item = MDListItem(
                MDListItemHeadlineText(text=barista.name, theme_text_color="Custom", text_color="black", bold=False),
                theme_bg_color="Custom",
                md_bg_color=bg_color,
                on_release=lambda x, b=barista: self.select_barista(b),
                size_hint_y=None,
                height="60dp"
            )
            list_view.add_widget(item)

        scroll_view.add_widget(list_view)

        bottom_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="70dp",
            padding=[0, 10, 0, 0]
        )

        back_button = MDButton(
            MDButtonIcon(icon="arrow-left-bold", theme_text_color="Custom", text_color="black"),
            MDButtonText(text="Назад", theme_text_color="Custom", text_color="black"),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color="pink",
            pos_hint={"center_x": 0.5}
        )
        back_button.bind(on_release=self.go_back)
        bottom_container.add_widget(back_button)

        main_layout.add_widget(title)
        main_layout.add_widget(scroll_view)  # Просто ScrollView вместо Card
        main_layout.add_widget(bottom_container)
        self.add_widget(main_layout)

    def select_barista(self, barista: Barista):
        dialog = MDDialog(
            MDDialogHeadlineText(text="Открыть смену", theme_text_color="Custom", text_color="black"),
            MDDialogSupportingText(text=f"Открыть смену для бариста {barista.name}?",
                                   theme_text_color="Custom", text_color="black"),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Отмена", theme_text_color="Custom", text_color="black"),
                    style="text",
                    # theme_bg_color="Custom",
                    # md_bg_color="pink",
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
        app.barista = barista
        app.shift = Shift(app.barista)

        self.manager.current = "main_menu"

        cafe_screen = self.manager.get_screen("main_menu")
        cafe_screen.update_for_barista(app.barista)

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
