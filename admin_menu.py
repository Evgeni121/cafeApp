from kivymd.uix.appbar import MDTopAppBarLeadingButtonContainer, MDTopAppBar, MDActionTopAppBarButton, \
    MDTopAppBarTrailingButtonContainer, MDTopAppBarTitle
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import MDDialog, MDDialogHeadlineText, MDDialogSupportingText, MDDialogButtonContainer
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen
from kivymd.uix.widget import MDWidget

from headers import TOP_APP_BAR_COLOR


class AdminMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "admin_menu"
        self.md_bg_color = "whitesmoke"

        self.top_app_bar = None
        self.toolbar_menu = None

        self.build_ui()

    def toolbar_menu_init(self):
        menu_items = [
            {
                "text": "Финансы",
                "leading_icon": "cash",
                "on_release": self.show_finance,
            },
            {
                "text": "Ингредиенты",
                "leading_icon": "sitemap",
                "on_release": self.show_ingredients,
            },
        ]

        self.toolbar_menu = MDDropdownMenu(
            items=menu_items,
        )

    def show_finance(self):
        pass

    def show_ingredients(self):
        pass

    def toolbar_menu_open(self, button):
        self.toolbar_menu.caller = button
        self.toolbar_menu.open()

    def top_app_bar_init(self):
        self.top_app_bar = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon="menu",
                    theme_text_color="Custom",
                    text_color="black",
                    on_release=self.toolbar_menu_open,
                )
            ),
            MDTopAppBarTitle(
                text=f"Меню администратора",
                theme_text_color="Custom",
                text_color="black",
                pos_hint={"center_x": .5},
            ),
            MDTopAppBarTrailingButtonContainer(
                MDActionTopAppBarButton(
                    icon="logout-variant",
                    theme_text_color="Custom",
                    text_color="black",
                    on_release=self.show_close_dialog,
                )
            ),
            theme_bg_color="Custom",
            md_bg_color=TOP_APP_BAR_COLOR
        )

        self.toolbar_menu_init()

    def build_ui(self):
        main_layout = MDBoxLayout(
            orientation="vertical",
        )

        content_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=10,
            padding=10,
        )

        self.top_app_bar_init()

        main_layout.add_widget(self.top_app_bar)
        main_layout.add_widget(content_layout)

        self.add_widget(main_layout)

    def show_close_dialog(self, *args):
        dialog = MDDialog(
            MDDialogHeadlineText(text="Выйти?", theme_text_color="Custom", text_color="black"),
            MDDialogSupportingText(text="Желаете выйти?\n\n", theme_text_color="Custom", text_color="black"),
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
                    on_release=lambda x: self.close(dialog)
                ),
            ),

            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )

        dialog.open()

    def close(self, dialog):
        dialog.dismiss()

        self.manager.current = "login_menu"
