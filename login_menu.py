from kivy.uix.image import Image
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDButtonIcon
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog, MDDialogButtonContainer, MDDialogContentContainer, MDDialogHeadlineText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldLeadingIcon
from kivy.metrics import dp
from kivymd.uix.widget import MDWidget


class LoginMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name = "login_menu"
        self.md_bg_color = "white"

        self.login_field = None
        self.password_field = None
        self.auth_dialog = None

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

        # НОВАЯ КНОПКА АДМИНИСТРАТОРА (добавлена снизу)
        admin_button = MDButton(
            MDButtonIcon(icon="shield-account", theme_text_color="Custom", text_color="gray"),
            MDButtonText(text="Администратор", theme_text_color="Custom", text_color="gray"),
            style="text",
            pos_hint={"center_x": 0.5},
            on_release=self.show_admin_auth,
            size_hint_y=None,
            height=dp(40)
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
        layout.add_widget(MDBoxLayout(size_hint_y=None, height=20))  # Отступ
        layout.add_widget(admin_button)  # Добавляем новую кнопку

        main_layout = MDRelativeLayout()
        main_layout.add_widget(layout)

        self.add_widget(main_layout)

    def show_admin_auth(self, *args):
        self.login_field = MDTextField(
            MDTextFieldLeadingIcon(
                icon="login",
            ),
            MDTextFieldHintText(
                text="Логин",
            ),
            text="admin",
            mode="outlined",
        )

        self.password_field = MDTextField(
            MDTextFieldLeadingIcon(
                icon="account-lock",
            ),
            MDTextFieldHintText(
                text="Пароль",
            ),
            mode="outlined",
            password=True,
        )

        """Показать диалог авторизации администратора"""
        self.auth_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Введите логин и пароль",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogContentContainer(
                self.login_field,
                self.password_field,
                orientation="vertical",
                spacing="12dp",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Отмена", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: self.auth_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Войти", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=self.process_admin_auth
                ),
            ),
            size_hint=(0.8, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        self.auth_dialog.open()

    def process_admin_auth(self, *args):
        """Обработка авторизации администратора"""
        login = self.login_field.text
        password = self.password_field.text

        # Ваша логика проверки
        if login == "admin" and password == "admin123":
            print("Успешная авторизация админа")
            # Переход на экран админа
            # self.manager.current = "admin_panel"
        else:
            print("Неверный логин или пароль")

        self.auth_dialog.dismiss()

    def go_to_barista_menu(self, *args):
        self.manager.current = "barista_menu"
