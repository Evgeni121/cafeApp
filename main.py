from typing import Optional

from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from barista_menu import BaristaMenuScreen, Barista
from login_menu import LoginMenuScreen
from main_menu import CafeMenuScreen, Product

PINK_COLOR = "pink"
TEXT_COLOR = "black"
BACKGROUND_COLOR = "white"


# ========== ГЛАВНОЕ ПРИЛОЖЕНИЕ ==========
class PigBankApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.barista: Optional[Barista] = None

        self.shift = None

        self.cart: [Product] = []

        self.orders = []

    def build(self):
        Window.size = (600, 750)

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Pink"

        screen_manager = MDScreenManager()
        screen_manager.add_widget(LoginMenuScreen())
        screen_manager.add_widget(BaristaMenuScreen())
        screen_manager.add_widget(CafeMenuScreen())

        screen_manager.current = "login_menu"
        return screen_manager


if __name__ == '__main__':
    PigBankApp().run()
