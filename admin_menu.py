from datetime import datetime, timedelta

from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.appbar import MDTopAppBarTrailingButtonContainer, MDActionTopAppBarButton, MDTopAppBarTitle, \
    MDTopAppBarLeadingButtonContainer, MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton, MDFabButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialogButtonContainer, MDDialogHeadlineText, MDDialog, MDDialogSupportingText, \
    MDDialogContentContainer
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItemHeadlineText, MDListItem, MDList, MDListItemSupportingText, \
    MDListItemLeadingIcon
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
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

        self.fab_button = None
        self.current_menu = None

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
        self.top_app_bar_title.text = "Кафе"

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
        self.current_menu = "Бариста"

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
                MDIconButton(
                    icon="dots-vertical",
                    theme_icon_color="Custom",
                    icon_color="black",
                    theme_bg_color="Custom",
                    md_bg_color="white",
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda x: ()
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                on_release=lambda x, b=barista: self.show_barista_shifts(b),
                size_hint_y=None,
                height=dp(80)
            )
            self.content_list.add_widget(barista_item)

    def show_barista_shifts(self, barista):
        self.current_menu = "Смены"

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
                MDIconButton(
                    icon="dots-vertical",
                    theme_icon_color="Custom",
                    icon_color="black",
                    theme_bg_color="Custom",
                    md_bg_color="white",
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda x: (),
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                size_hint_y=None,
                height=dp(120)
            )
            self.content_list.add_widget(stats_item)

    def show_finance(self):
        self.current_menu = "Финансы"

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
            {"period": "Все время", "income": 500000, "expenses": 105000},
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
                MDIconButton(
                    icon="dots-vertical",
                    theme_icon_color="Custom",
                    icon_color="black",
                    theme_bg_color="Custom",
                    md_bg_color="white",
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda x: (),
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                size_hint_y=None,
                height=dp(120)
            )
            self.content_list.add_widget(finance_item)

    def show_ingredients(self):
        self.current_menu = "Ингредиенты"

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
            orientation="vertical",
            spacing=10,
            padding=10,
        )

        self.top_app_bar_init()
        self.content_panel_init()

        # Создаем кнопку +
        self.fab_button = MDFabButton(
            icon="plus",
            theme_bg_color="Custom",
            md_bg_color="pink",
            theme_text_color="Custom",
            text_color="black",
            pos_hint={"center_x": 0.9, "center_y": 0.1},
            on_release=self.on_fab_click
        )

        content_layout.add_widget(self.content_panel)
        content_layout.add_widget(self.fab_button)

        main_layout.add_widget(self.top_app_bar)
        main_layout.add_widget(content_layout)

        self.add_widget(main_layout)

    def on_fab_click(self, *args):
        if self.current_menu == "Бариста":
            self.show_add_barista_dialog()
        elif self.current_menu == "Финансы":
            self.show_add_finance_dialog()
        elif self.current_menu == "Ингредиенты":
            self.show_add_ingredient_dialog()
        else:
            self.show_fab_menu()

    def show_fab_menu(self):
        """Показать меню выбора при клике в главном меню"""
        from kivymd.uix.menu import MDDropdownMenu

        menu_items = [
            {
                "text": "Добавить бариста",
                "leading_icon": "account-plus",
                "on_release": self.show_add_barista_dialog
            },
            {
                "text": "Добавить ингредиент",
                "leading_icon": "water-plus",
                "on_release": self.show_add_ingredient_dialog
            },
            {
                "text": "Добавить расходы",
                "leading_icon": "cash-plus",
                "on_release": self.show_add_finance_dialog
            },
        ]

        self.fab_menu = MDDropdownMenu(
            items=menu_items,
            caller=self.fab_button,
        )
        self.fab_menu.open()

    def show_add_barista_dialog(self):
        """Диалог добавления нового бариста"""
        self.barista_name_input = MDTextField(
            MDTextFieldHintText(
                text="Имя",
            ),
            mode="outlined"
        )

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Введите имя",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogContentContainer(
                self.barista_name_input,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Отмена", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Добавить", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: self.add_new_barista(dialog)
                ),
            ),
            size_hint=(0.8, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def add_new_barista(self, dialog):
        """Добавить нового бариста в БД"""
        name = self.barista_name_input.text.strip()

        if name:
            # Добавляем в базу данных
            barista = Barista(barista_id=0, name=name)
            # barista.save()  # Ваш метод сохранения

            # Закрываем диалог
            dialog.dismiss()

            # Обновляем список бариста
            self.show_baristas()

            # Показываем уведомление
            from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
            MDSnackbar(
                MDSnackbarText(text=f"Бариста '{name}' добавлен", theme_text_color="Custom", text_color="black"),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.7,
                theme_bg_color="Primary",
                radius=[10, 10, 10, 10],
                duration=1,
            ).open()

    def show_add_finance_dialog(self):
        """Диалог добавления финансовой операции"""
        self.finance_type = "income"  # income/expense

        self.finance_description = MDTextField(
            hint_text="Описание операции",
            mode="outlined",
            size_hint_x=0.9
        )

        self.finance_amount = MDTextField(
            hint_text="Сумма (BYN)",
            mode="outlined",
            input_filter="int",
            size_hint_x=0.9
        )

        # Контейнер для типа операции
        type_container = MDBoxLayout(
            orientation="horizontal",
            spacing=10,
            size_hint_x=0.9
        )

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Введите название и сумму",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogContentContainer(
                self.finance_description,
                self.finance_amount,
                orientation="vertical",
                spacing=15
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Отмена", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Добавить", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: self.add_new_finance(dialog)
                ),
            ),
            size_hint=(0.8, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def set_finance_type(self, ftype):
        """Установить тип финансовой операции"""
        self.finance_type = ftype
        if ftype == "income":
            self.income_btn.md_bg_color = "green"
            self.expense_btn.md_bg_color = "lightgray"
        else:
            self.income_btn.md_bg_color = "lightgray"
            self.expense_btn.md_bg_color = "red"

    def add_new_finance(self, dialog):
        """Добавить финансовую операцию"""
        description = self.finance_description.text.strip()
        amount = self.finance_amount.text.strip()

        if description and amount:
            try:
                # Здесь ваша логика сохранения в БД
                amount_int = int(amount)
                print(f"Добавляем {self.finance_type}: {description} - {amount_int} BYN")

                dialog.dismiss()
                self.show_finance()  # Обновляем список

                # Уведомление
                from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
                MDSnackbar(
                    MDSnackbarText(
                        text=f"Операция '{description}' добавлена",
                        theme_text_color="Custom",
                        text_color="black"
                    ),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.7,
                    theme_bg_color="Primary",
                    radius=[10, 10, 10, 10],
                    duration=1,
                ).open()

            except ValueError:
                print("Ошибка: сумма должна быть числом")

    def show_add_ingredient_dialog(self):
        """Диалог добавления нового ингредиента"""
        self.ingredient_name = MDTextField(
            hint_text="Название ингредиента",
            mode="outlined",
            size_hint_x=0.9
        )

        self.ingredient_quantity = MDTextField(
            hint_text="Количество (мл)",
            mode="outlined",
            input_filter="int",
            size_hint_x=0.9
        )

        self.ingredient_min_quantity = MDTextField(
            hint_text="Минимальный запас (мл)",
            mode="outlined",
            input_filter="int",
            size_hint_x=0.9
        )

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Введите параметры ингредиента",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogContentContainer(
                self.ingredient_name,
                self.ingredient_quantity,
                self.ingredient_min_quantity,
                orientation="vertical",
                spacing=15
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Отмена", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Добавить", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: self.add_new_ingredient(dialog)
                ),
            ),
            size_hint=(0.8, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def add_new_ingredient(self, dialog):
        """Добавить новый ингредиент"""
        name = self.ingredient_name.text.strip()
        quantity = self.ingredient_quantity.text.strip()
        min_quantity = self.ingredient_min_quantity.text.strip()

        if name and quantity:
            try:
                quantity_int = int(quantity)
                min_quantity_int = int(min_quantity) if min_quantity else 0

                # Здесь ваша логика сохранения в БД
                # ingredient = Ingredient(name=name, amount=quantity_int, min_amount=min_quantity_int)
                # ingredient.save()

                print(f"Добавляем ингредиент: {name} - {quantity_int} мл")

                dialog.dismiss()
                self.show_ingredients()  # Обновляем список

                # Уведомление
                from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
                MDSnackbar(
                    MDSnackbarText(
                        text=f"Ингредиент '{name}' добавлен",
                        theme_text_color="Custom",
                        text_color="black"
                    ),
                    y=dp(24),
                    pos_hint={"center_x": 0.5},
                    size_hint_x=0.7,
                    theme_bg_color="Primary",
                    radius=[10, 10, 10, 10],
                    duration=1,
                ).open()

            except ValueError:
                print("Ошибка: количество должно быть числом")

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
