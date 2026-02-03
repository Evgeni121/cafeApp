from datetime import datetime, timedelta

from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.appbar import MDTopAppBarTrailingButtonContainer, MDActionTopAppBarButton, MDTopAppBarTitle, \
    MDTopAppBarLeadingButtonContainer, MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialogButtonContainer, MDDialogHeadlineText, MDDialog, MDDialogSupportingText
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItemHeadlineText, MDListItem, MDList, MDListItemSupportingText, \
    MDListItemLeadingIcon
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.widget import MDWidget

from headers import TOP_APP_BAR_COLOR, Ingredient, Barista, SECONDARY_COLOR


class AdminMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "admin_menu"
        self.md_bg_color = "whitesmoke"

        self.top_app_bar = None

        self.content_panel = None
        self.content_list = None

        self.back_button_place = None
        self.top_app_bar_title = None

        self.build_ui()

    def add_back_button(self):
        button = MDActionTopAppBarButton(
            icon="arrow-left",
            theme_text_color="Custom",
            text_color="black",
            on_release=lambda x: self.go_back(),
        )

        self.back_button_place.add_widget(button)

    def delete_back_button(self):
        self.back_button_place.clear_widgets()

    def top_app_bar_init(self):
        self.back_button_place = MDTopAppBarLeadingButtonContainer()
        self.top_app_bar_title = MDTopAppBarTitle(
                text="Меню администратора",
                theme_text_color="Custom",
                text_color="black",
            )

        self.top_app_bar = MDTopAppBar(
            self.back_button_place,
            self.top_app_bar_title,
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

    def go_back(self):
        self.show_main_menu()

    def show_main_menu(self):
        # Скрываем кнопку назад
        self.delete_back_button()
        self.top_app_bar_title.text = "Меню"

        # Очищаем контент
        self.content_list.clear_widgets()

        # Добавляем элементы главного меню
        menu_items = [
            {"icon": "clock-time-three", "title": "Смены", "subtitle": "Смены бариста", "action": self.show_baristas},
            {"icon": "cash", "title": "Финансы", "subtitle": "Статистика", "action": self.show_finance},
            {"icon": "sitemap", "title": "Ингредиенты", "subtitle": "Остатки", "action": self.show_ingredients},
        ]

        for item in menu_items:
            menu_item = MDListItem(
                MDListItemLeadingIcon(
                    icon=item["icon"],
                ),
                MDListItemHeadlineText(
                    text=item["title"],
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDListItemSupportingText(
                    text=item["subtitle"],
                    theme_text_color="Custom",
                    text_color="gray",
                ),
                divider=True,
                divider_color="black",
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                on_release=lambda x, i=item: i["action"](),
                size_hint_y=None,
                height=dp(80)
            )
            self.content_list.add_widget(menu_item)

    def content_panel_init(self):
        self.content_panel = MDBoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10,
            radius=[10, 10, 10, 10],
            theme_bg_color="Custom",
            md_bg_color=TOP_APP_BAR_COLOR
        )

        self.content_list = MDList(
            spacing=10,
            padding=10,
        )

        scroll = MDScrollView()
        scroll.add_widget(self.content_list)

        self.content_panel.add_widget(scroll)

        # Показываем главное меню
        self.show_main_menu()

    def show_baristas(self):
        self.add_back_button()
        self.top_app_bar_title.text = "Бариста"

        # Очищаем контент
        self.content_list.clear_widgets()

        baristas = Barista.get_all_baristas()

        if not baristas:
            empty_item = MDListItem(
                MDListItemLeadingIcon(icon="account-off"),
                MDListItemHeadlineText(
                    text="Бариста отсутствуют",
                    theme_text_color="Custom",
                    text_color="black",
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                size_hint_y=None,
                height=dp(80)
            )
            self.content_list.add_widget(empty_item)
            return

        for barista in baristas:
            barista_item = MDListItem(
                MDListItemLeadingIcon(
                    icon="account",
                ),
                MDListItemHeadlineText(
                    text=barista.name,
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDListItemSupportingText(
                    text="Смены",
                    theme_text_color="Custom",
                    text_color="gray",
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                on_release=lambda x, b=barista: self.show_barista_shifts(b),
                size_hint_y=None,
                height=dp(80)
            )
            self.content_list.add_widget(barista_item)

    def show_barista_shifts(self, barista):
        self.top_app_bar_title.text = "Смены"

        # Очищаем контент
        self.content_list.clear_widgets()

        app = MDApp.get_running_app()
        shifts = app.shift.get_all_shifts(barista) if hasattr(app, 'shift') else []

        # Заголовок
        header_item = MDListItem(
            MDListItemLeadingIcon(
                icon="account",
            ),
            MDListItemHeadlineText(
                text=barista.name,
                theme_text_color="Custom",
                text_color="black",
            ),
            MDListItemSupportingText(
                text="История смен",
                theme_text_color="Custom",
                text_color="gray",
            ),
            theme_bg_color="Custom",
            md_bg_color="pink",
            size_hint_y=None,
            height=dp(100)
        )
        self.content_list.add_widget(header_item)

        total_income = 0
        total_expenses = 0

        if not shifts:
            no_shifts_item = MDListItem(
                MDListItemLeadingIcon(icon="clock-off"),
                MDListItemHeadlineText(
                    text="Нет смен",
                    theme_text_color="Custom",
                    text_color="black",
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                size_hint_y=None,
                height=dp(80)
            )
            self.content_list.add_widget(no_shifts_item)
        else:
            for shift in shifts:
                income = shift.income if hasattr(shift, 'income') else 0
                expenses = shift.expenses if hasattr(shift, 'expenses') else 0
                total_income += income
                total_expenses += expenses

                shift_date = shift.date if hasattr(shift, 'date') else "Дата неизвестна"

                shift_item = MDListItem(
                    MDListItemLeadingIcon(
                        icon="clock",
                    ),
                    MDListItemHeadlineText(
                        text=f"Смена: {shift_date}",
                        theme_text_color="Custom",
                        text_color="black",
                    ),
                    MDListItemSupportingText(
                        text=f"Доход: {income} ₽ | Расходы: {expenses} ₽",
                        theme_text_color="Custom",
                        text_color="gray",
                    ),
                    theme_bg_color="Custom",
                    md_bg_color=TOP_APP_BAR_COLOR,
                    size_hint_y=None,
                    height=dp(100)
                )
                self.content_list.add_widget(shift_item)

        # Статистика
        if shifts:
            stats_item = MDListItem(
                MDListItemLeadingIcon(
                    icon="chart-box",
                ),
                MDListItemHeadlineText(
                    text="Общая статистика:",
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDListItemSupportingText(
                    text=f"Всего смен: {len(shifts)}",
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDListItemSupportingText(
                    text=f"Доход: {total_income} ₽ | Расходы: {total_expenses} ₽",
                    theme_text_color="Custom",
                    text_color="gray",
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                size_hint_y=None,
                height=dp(120)
            )
            self.content_list.add_widget(stats_item)

    def show_finance(self):
        # Показываем кнопку назад
        self.add_back_button()
        self.top_app_bar_title.text = "Финансы"

        # Очищаем контент
        self.content_list.clear_widgets()

        # Заглушки для данных
        finance_data = [
            {"period": "Сегодня", "income": 15000, "expenses": 5000},
            {"period": "Неделя", "income": 85000, "expenses": 25000},
            {"period": "Месяц", "income": 320000, "expenses": 95000},
        ]

        for data in finance_data:
            profit = data['income'] - data['expenses']

            finance_item = MDListItem(
                MDListItemLeadingIcon(
                    icon="cash",
                ),
                MDListItemHeadlineText(
                    text=data["period"],
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDListItemSupportingText(
                    text=f"Доход: {data['income']} ₽",
                    theme_text_color="Custom",
                    text_color="green",
                ),
                MDListItemSupportingText(
                    text=f"Расходы: {data['expenses']} ₽",
                    theme_text_color="Custom",
                    text_color="red",
                ),
                MDListItemSupportingText(
                    text=f"Прибыль: {profit} ₽",
                    theme_text_color="Custom",
                    text_color="purple" if profit > 0 else "red",
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                size_hint_y=None,
                height=dp(120)
            )
            self.content_list.add_widget(finance_item)

    def show_ingredients(self):
        # Показываем кнопку назад
        self.add_back_button()
        self.top_app_bar_title.text = "Ингредиенты"

        # Очищаем контент
        self.content_list.clear_widgets()

        ingredients = Ingredient.get_all()

        # Статистика
        low_stock_count = sum(1 for i in ingredients if i.amount < 1)
        total_ingredients = len(ingredients)

        stats_item = MDListItem(
            MDListItemLeadingIcon(
                icon="sitemap",
            ),
            MDListItemHeadlineText(
                text="Статистика ингредиентов:",
                theme_text_color="Custom",
                text_color="black",
            ),
            MDListItemSupportingText(
                text=f"Всего: {total_ingredients}",
                theme_text_color="Custom",
                text_color="black",
            ),
            MDListItemSupportingText(
                text=f"Заканчиваются: {low_stock_count}",
                theme_text_color="Custom",
                text_color="red" if low_stock_count > 0 else "gray",
            ),
            theme_bg_color="Custom",
            md_bg_color="pink" if low_stock_count > 0 else TOP_APP_BAR_COLOR,
            size_hint_y=None,
            height=dp(100)
        )
        self.content_list.add_widget(stats_item)

        # Список ингредиентов
        for ingredient in ingredients:
            is_low = ingredient.amount < 1

            ingredient_item = MDListItem(
                MDListItemLeadingIcon(
                    icon="water",
                ),
                MDListItemHeadlineText(
                    text=ingredient.name,
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDListItemSupportingText(
                    text=f"Остаток: {ingredient.amount} мл",
                    theme_text_color="Custom",
                    text_color="red" if is_low else "black",
                ),
                MDListItemSupportingText(
                    text="⚠ ЗАКАНЧИВАЕТСЯ" if is_low else "✓ В НАЛИЧИИ",
                    theme_text_color="Custom",
                    text_color="red" if is_low else "green",
                ),
                theme_bg_color="Custom",
                md_bg_color="red" if is_low else TOP_APP_BAR_COLOR,
                size_hint_y=None,
                height=dp(100)
            )
            self.content_list.add_widget(ingredient_item)

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
        self.content_panel_init()

        content_layout.add_widget(self.content_panel)

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
