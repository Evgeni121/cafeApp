from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from admin_menu import AdminMenuScreen
from barista_menu import BaristaMenuScreen
from headers import Shift, Cart, Menu
from login_menu import LoginMenuScreen
from main_menu import MainMenuScreen


class PigBankApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.menu: Menu = Menu()

        self.cart: Cart = Cart()

        self.shift: Shift = Shift()
        self.shift.get_today_shift()

    def build(self):
        Window.size = (500, 700)

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Pink"

        screen_manager = MDScreenManager()

        screen_manager.add_widget(LoginMenuScreen())
        screen_manager.add_widget(BaristaMenuScreen())
        screen_manager.add_widget(AdminMenuScreen())
        screen_manager.add_widget(MainMenuScreen())

        if self.shift.is_active:
            screen_manager.current = "main_menu"
        else:
            screen_manager.current = "login_menu"

        return screen_manager


PigBankApp().run()
