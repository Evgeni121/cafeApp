from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.appbar import MDTopAppBarTrailingButtonContainer, MDActionTopAppBarButton, MDTopAppBarTitle, \
    MDTopAppBarLeadingButtonContainer, MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton, MDFabButton
from kivymd.uix.dialog import MDDialogButtonContainer, MDDialogHeadlineText, MDDialog, MDDialogSupportingText, \
    MDDialogContentContainer
from kivymd.uix.list import MDListItemHeadlineText, MDListItem, MDList, MDListItemSupportingText, \
    MDListItemLeadingIcon, MDListItemTertiaryText
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText, MDTextFieldHelperText
from kivymd.uix.widget import MDWidget
from kivymd.uix.menu import MDDropdownMenu

from headers import TOP_APP_BAR_COLOR, Ingredient, Barista, Drink, MenuDrink


class AdminMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "admin_menu"
        self.md_bg_color = "whitesmoke"

        self.top_app_bar = None

        self.content_panel = None

        self.back_button_place = None
        self.top_app_bar_title = None

        self.fab_button = None
        self.current_menu = None

        self.trailing_buttons = None

        self.barista_name_input = None
        self.finance_description = None
        self.finance_amount = None

        self.ingredient_name = None
        self.ingredient_volume = None
        self.ingredient_price = None
        self.ingredient_calories = None
        self.ingredient_dropdown_menu = None

        self.search_dialog = None
        self.search_input = None

        self.build_ui()

    def add_back_button(self):
        if not self.back_button_place.children:
            button = MDActionTopAppBarButton(
                icon="arrow-left",
                theme_text_color="Custom",
                text_color="black",
                on_release=lambda x: self.go_back(),
            )

            self.back_button_place.add_widget(button)

    def delete_back_button(self):
        self.back_button_place.clear_widgets()

    def filter_ingredients(self, search_text):
        """Фильтрация ингредиентов"""
        ingredients = Ingredient.get_all()

        if search_text:
            # Фильтруем по названию
            ingredients = [i for i in ingredients if search_text.lower() in i.name.lower()]

        # Очищаем контент
        self.content_panel.clear_widgets()

        content_list = MDList(
            spacing=10,
            padding=10,
        )

        total_ingredients = len(ingredients)

        header = MDListItem(
            MDListItemLeadingIcon(
                icon="coffee",
            ),
            MDListItemHeadlineText(
                text="Ингредиенты" + (f" - поиск: '{search_text}'" if search_text else ""),
                theme_text_color="Custom",
                text_color="black",
            ),
            MDListItemSupportingText(
                text=f"Найдено: {total_ingredients}",
                theme_text_color="Custom",
                text_color="black",
            ),
            theme_bg_color="Custom",
            md_bg_color=TOP_APP_BAR_COLOR,
            on_release=lambda x: (),
        )

        self.content_panel.add_widget(header)

        # Список ингредиентов
        for ingredient in ingredients:
            is_low = ingredient.amount < 1

            ingredient_item = MDListItem(
                MDListItemLeadingIcon(
                    icon="coffee",
                ),
                MDListItemHeadlineText(
                    text=ingredient.name,
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDListItemSupportingText(
                    text="ЗАКАНЧИВАЕТСЯ" if is_low else "В НАЛИЧИИ",
                    theme_text_color="Custom",
                    text_color="red" if is_low else "green",
                ),
                MDListItemSupportingText(
                    text=f"Остаток: {ingredient.amount} мл",
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDIconButton(
                    icon="dots-vertical",
                    theme_icon_color="Custom",
                    icon_color="black",
                    theme_bg_color="Custom",
                    md_bg_color="white",
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda x, i=ingredient: self.ingredient_menu(x, i),
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                on_release=lambda x: ()
            )
            content_list.add_widget(ingredient_item)

        scroll = MDScrollView()
        scroll.add_widget(content_list)

        self.content_panel.add_widget(scroll)

    def toggle_search(self, *args):
        pass

    def top_app_bar_init(self):
        self.back_button_place = MDTopAppBarLeadingButtonContainer()

        self.top_app_bar_title = MDTopAppBarTitle(
            text="Меню администратора",
            theme_text_color="Custom",
            text_color="black",
        )

        self.trailing_buttons = MDTopAppBarTrailingButtonContainer(
            MDActionTopAppBarButton(
                icon="magnify",
                theme_text_color="Custom",
                text_color="black",
                on_release=self.toggle_search,
            ),
            MDActionTopAppBarButton(
                icon="logout-variant",
                theme_text_color="Custom",
                text_color="black",
                on_release=self.show_close_dialog,
            )
        )

        self.top_app_bar = MDTopAppBar(
            self.back_button_place,
            self.top_app_bar_title,
            self.trailing_buttons,
            theme_bg_color="Custom",
            md_bg_color=TOP_APP_BAR_COLOR
        )

    def go_back(self):
        if self.current_menu == "Смены":
            self.show_baristas()
        elif self.current_menu == "Напитки":
            self.show_menu()
        elif self.current_menu == "Рецепт":
            pass
        else:
            self.show_main_menu()

    def show_main_menu(self):
        self.current_menu = "Главное меню"

        # Скрываем кнопку назад
        self.delete_back_button()
        self.top_app_bar_title.text = "Меню администратора"

        # Очищаем контент
        self.content_panel.clear_widgets()

        content_list = MDList(
            spacing=10,
            padding=10,
        )

        # Добавляем элементы главного меню
        menu_items = [
            {"icon": "coffee", "title": "Меню", "subtitle": "Категории | напитки | десерты", "action": self.show_menu},
            {"icon": "clock-time-three", "title": "Смены", "subtitle": "Смены бариста", "action": self.show_baristas},
            {"icon": "cash", "title": "Финансы", "subtitle": "Выручка | расходы | прибыль",
             "action": self.show_finance},
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
                on_release=lambda x, f=item["action"]: f(),
            )
            content_list.add_widget(menu_item)

        scroll = MDScrollView()
        scroll.add_widget(content_list)

        self.content_panel.add_widget(scroll)

    def content_panel_init(self):
        self.content_panel = MDBoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10,
            radius=[10, 10, 10, 10],
            theme_bg_color="Custom",
            md_bg_color=TOP_APP_BAR_COLOR
        )

        # Показываем главное меню
        self.show_main_menu()

    def show_baristas(self):
        self.current_menu = "Бариста"

        self.add_back_button()

        self.top_app_bar_title.text = "Бариста"

        # Очищаем контент
        self.content_panel.clear_widgets()

        content_list = MDList(
            spacing=10,
            padding=10,
        )

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
            )
            content_list.add_widget(empty_item)
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
            )
            content_list.add_widget(barista_item)

        scroll = MDScrollView()
        scroll.add_widget(content_list)

        self.content_panel.add_widget(scroll)

    def show_barista_shifts(self, barista):
        self.current_menu = "Смены"
        self.top_app_bar_title.text = "Смены"

        # Очищаем контент
        self.content_panel.clear_widgets()

        content_list = MDList(
            spacing=10,
            padding=10,
        )

        app = MDApp.get_running_app()
        shifts = app.shift.get_all_shifts(barista) if hasattr(app, 'shift') else []

        total_hours = 0
        total_revenue = 0
        total_order_amount = 0

        for shift in shifts:
            total_hours += shift.total_hours
            total_revenue += shift.revenue
            total_order_amount += shift.order_amount

        header = MDListItem(
            MDListItemLeadingIcon(
                icon="account",
            ),
            MDListItemHeadlineText(
                text=barista.name,
                theme_text_color="Custom",
                text_color="black",
            ),
            MDListItemSupportingText(
                text=f"Всего смен: {len(shifts)}",
                theme_text_color="Custom",
                text_color="black",
            ),
            MDListItemSupportingText(
                text=f"Заказов: {total_order_amount} | Выручка: {total_revenue} BYN | Часы: {total_hours}",
                theme_text_color="Custom",
                text_color="gray",
            ),
            theme_bg_color="Custom",
            md_bg_color=TOP_APP_BAR_COLOR,
            on_release=lambda x: (),
        )

        self.content_panel.add_widget(header)

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
            )
            content_list.add_widget(no_shifts_item)
        else:
            for shift in reversed(shifts):
                shift_item = MDListItem(
                    MDListItemLeadingIcon(
                        icon="clock",
                    ),
                    MDListItemHeadlineText(
                        text=f"Смена: {shift.start_time.strftime('%d.%m.%Y')}",
                        theme_text_color="Custom",
                        text_color="black",
                    ),
                    MDListItemSupportingText(
                        text=f"Заказов: {shift.order_amount} | Выручка: {shift.revenue} BYN | Часы: {shift.total_hours}",
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
                    on_release=lambda x: ()
                )
                content_list.add_widget(shift_item)

        scroll = MDScrollView()
        scroll.add_widget(content_list)

        self.content_panel.add_widget(scroll)

    def show_finance(self):
        self.current_menu = "Финансы"

        # Показываем кнопку назад
        self.add_back_button()
        self.top_app_bar_title.text = "Финансы"

        # Очищаем контент
        self.content_panel.clear_widgets()

        content_list = MDList(
            spacing=10,
            padding=10,
        )

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
                    text=f"Выручка: {data['income']} BYN | Расходы: {data['expenses']} BYN",
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDListItemTertiaryText(
                    text=f"Прибыль: {profit} BYN",
                    theme_text_color="Custom",
                    text_color="green" if profit > 0 else "red",
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
                on_release=lambda x: ()
            )
            content_list.add_widget(finance_item)

        scroll = MDScrollView()
        scroll.add_widget(content_list)

        self.content_panel.add_widget(scroll)

    def ingredient_menu(self, button, ingredient):
        ingredient_menu = [
            {
                "text": "Поступление",
                "leading_icon": "water-plus",
                "on_release": lambda x=None, i=ingredient: self.ingredient_arrival(i),
            },
            {
                "text": "Списание",
                "leading_icon": "water-minus",
                "on_release": lambda x=None, i=ingredient: self.ingredient_write_off(i),
            },
            {
                "text": "Удалить",
                "leading_icon": "trash-can-outline",
                "on_release": lambda x=None, i=ingredient: self.ingredient_delete(i),
            },
        ]

        self.ingredient_dropdown_menu = MDDropdownMenu(items=ingredient_menu)
        self.ingredient_dropdown_menu.caller = button
        self.ingredient_dropdown_menu.open()

    def on_search_text_changed(self, instance, value):
        self.load_ingredients_list(value)

    def ingredient_arrival(self, ingredient):
        """Добавить приход ингредиента"""
        self.ingredient_dropdown_menu.dismiss()

        volume_input = MDTextField(
            MDTextFieldHintText(
                text="Объем, шт/мл/г",
                theme_text_color="Custom",
                text_color="black"
            ),
            mode="outlined",
            input_filter="int",
        )

        price_input = MDTextField(
            MDTextFieldHintText(
                text="Сумма, BYN",
                theme_text_color="Custom",
                text_color="black"
            ),
            mode="outlined",
            input_filter="float",
        )

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Поступление",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogSupportingText(
                text="Введите объем и сумму",
                theme_text_color="Custom",
                text_color="grey"
            ),
            MDDialogContentContainer(
                volume_input,
                price_input,
                spacing=15,
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
                    on_release=lambda x: self.process_ingredient_arrival(dialog, ingredient, volume_input, price_input)
                ),
            ),
            size_hint=(0.8, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def refresh_ingredients_list(self):
        if hasattr(self, 'search_input') and self.search_input:
            current_search = self.search_input.text
            self.load_ingredients_list(current_search)

    def process_ingredient_arrival(self, dialog, ingredient, volume_input, price_input):
        volume = volume_input.text.strip()
        price = price_input.text.strip()

        if volume and price:
            try:
                volume = int(volume)
                price = float(price)

                dialog.dismiss()

                # Обновляем список с сохранением поиска
                self.refresh_ingredients_list()

                MDSnackbar(
                    MDSnackbarText(
                        text=f"Добавлено {volume} шт/мл/г {ingredient.name}",
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

            except ValueError as e:
                volume_input.error = True
                MDSnackbar(
                    MDSnackbarText(
                        text="Введите корректное количество",
                        theme_text_color="Custom",
                        text_color="black"
                    ),
                    duration=1,
                ).open()
        else:
            if not volume:
                volume_input.error = True

            if not price:
                price_input.error = True

    def ingredient_write_off(self, ingredient):
        """Списать ингредиент"""
        self.ingredient_dropdown_menu.dismiss()

        # Создаем поле для ввода количества списания
        volume_input = MDTextField(
            MDTextFieldHintText(
                text=f"Объем, шт/мл/г",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDTextFieldHelperText(
                text=f"Доступно: {ingredient.amount} шт/мл/г",
                mode="persistent",
            ),
            mode="outlined",
            input_filter="int",
        )

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Списание",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogSupportingText(
                text="Введите объем",
                theme_text_color="Custom",
                text_color="grey"
            ),
            MDDialogContentContainer(
                volume_input,
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
                    MDButtonText(text="Списать", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: self.process_ingredient_write_off(dialog, ingredient, volume_input)
                ),
            ),
            size_hint=(0.8, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def process_ingredient_write_off(self, dialog, ingredient, volume_input):
        volume = volume_input.text.strip()
        if volume:
            try:
                volume = int(volume)

                if volume > ingredient.amount:
                    raise ValueError(f"Доступно: {ingredient.amount} шт/мл/г")

                dialog.dismiss()

                self.refresh_ingredients_list()

                MDSnackbar(
                    MDSnackbarText(
                        text=f"Списано {volume} шт/мл/г {ingredient.name}",
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

            except ValueError as e:
                volume_input.error = True
                MDSnackbar(
                    MDSnackbarText(
                        text=str(e) if str(e) else "Введите корректное количество",
                        theme_text_color="Custom",
                        text_color="black"
                    ),
                    duration=2,
                ).open()
        else:
            if not volume:
                volume_input.error = True

    def ingredient_delete(self, ingredient):
        self.ingredient_dropdown_menu.dismiss()

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Удалить ингредиент?",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogSupportingText(
                text=f"Вы уверены, что хотите удалить {ingredient.name}?",
                theme_text_color="Custom",
                text_color="grey"
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Отмена", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Удалить", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: self.process_ingredient_delete(dialog, ingredient)
                ),
            ),
            size_hint=(0.8, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def process_ingredient_delete(self, dialog, ingredient):
        dialog.dismiss()

        # Обновляем список с сохранением поиска
        self.refresh_ingredients_list()

        MDSnackbar(
            MDSnackbarText(
                text=f"Ингредиент {ingredient.name} удален успешно!",
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

    def load_ingredients_list(self, search_text=""):
        self.ingredients_content_list.clear_widgets()

        all_ingredients = Ingredient.get_all()
        total_all = len(all_ingredients)

        if search_text:
            search_lower = search_text.lower()
            ingredients = [
                i for i in all_ingredients
                if search_lower in i.name.lower()
            ]
        else:
            ingredients = all_ingredients

        found_count = len(ingredients)  # Количество найденных

        if hasattr(self, 'search_input') and self.search_input:
            # Ищем HelperText внутри search_input
            for child in self.search_input.children:
                if isinstance(child, MDTextFieldHelperText):
                    if search_text:
                        child.text = f"Найдено: {found_count} из {total_all}"
                    else:
                        child.text = f"Всего: {total_all}"
                    break

        # Отображаем результат
        if not ingredients:
            empty_item = MDListItem(
                MDListItemLeadingIcon(icon="magnify-close"),
                MDListItemHeadlineText(
                    text="Ничего не найдено" if search_text else "Нет ингредиентов",
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDListItemSupportingText(
                    text="Попробуйте изменить запрос" if search_text else "Добавьте первый ингредиент",
                    theme_text_color="Custom",
                    text_color="gray",
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
            )
            self.ingredients_content_list.add_widget(empty_item)
            return

        # Добавляем каждый ингредиент
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
                    text="ЗАКАНЧИВАЕТСЯ" if is_low else "В НАЛИЧИИ",
                    theme_text_color="Custom",
                    text_color="red" if is_low else "green",
                ),
                MDListItemSupportingText(
                    text=f"Остаток: {ingredient.amount} мл",
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDIconButton(
                    icon="dots-vertical",
                    theme_icon_color="Custom",
                    icon_color="black",
                    theme_bg_color="Custom",
                    md_bg_color="white",
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda x, i=ingredient: self.ingredient_menu(x, i),
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
            )
            self.ingredients_content_list.add_widget(ingredient_item)

    def show_drink_menu(self, menu_drink: MenuDrink):
        self.current_menu = "Рецепт"

        self.add_back_button()
        self.top_app_bar_title.text = f"Рецепт {menu_drink.name}"

        self.content_panel.clear_widgets()

        length = len(menu_drink.drinks)
        drinks = sorted(menu_drink.drinks, key=lambda x: x.size)

        main_text = f"{menu_drink.name}     {drinks[0].price} | {drinks[1].price} BYN" \
            if length > 1 else f"{menu_drink.name}     {drinks[0].price} BYN"

        support_text = f"{drinks[0].size} | {drinks[1].size} {drinks[0].size_unit}" \
            if length > 1 else f"{drinks[0].size} {drinks[0].size_unit}"

        # Информация о напитке
        drink_info = MDListItem(
            MDListItemLeadingIcon(icon="coffee"),
            MDListItemHeadlineText(
                text=menu_drink.name,
                theme_text_color="Custom",
                text_color="black",
            ),
            MDListItemSupportingText(
                text=main_text,
                theme_text_color="Custom",
                text_color="gray",
            ),
            MDListItemTertiaryText(
                text=support_text,
                theme_text_color="Custom",
                text_color="gray",
            ),
            theme_bg_color="Custom",
            md_bg_color=TOP_APP_BAR_COLOR,
        )

        self.content_panel.add_widget(drink_info)

        # Заголовок списка ингредиентов
        ingredients_header = MDListItem(
            MDListItemLeadingIcon(icon="food-apple"),
            MDListItemHeadlineText(
                text="Ингредиенты в составе",
                theme_text_color="Custom",
                text_color="black",
            ),
            MDListItemSupportingText(
                text=f"Всего: {len(menu_drink.ingredients)}",
                theme_text_color="Custom",
                text_color="gray",
            ),
            theme_bg_color="Custom",
            md_bg_color=TOP_APP_BAR_COLOR,
        )

        self.content_panel.add_widget(ingredients_header)

        # Список ингредиентов
        content_list = MDList(
            spacing=10,
            padding=10,
        )

        if not menu_drink.ingredients:
            empty_item = MDListItem(
                MDListItemLeadingIcon(icon="food-off"),
                MDListItemHeadlineText(
                    text="Нет ингредиентов",
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDListItemSupportingText(
                    text="Добавьте ингредиенты через меню",
                    theme_text_color="Custom",
                    text_color="gray",
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
            )
            content_list.add_widget(empty_item)
        else:
            for ingredient_data in menu_drink.ingredients:
                ingredient = ingredient_data['ingredient']
                amount = ingredient_data['amount']

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
                        text=f"Количество: {amount} мл",
                        theme_text_color="Custom",
                        text_color="gray",
                    ),
                    MDListItemTertiaryText(
                        text=f"Остаток: {ingredient.amount} мл",
                        theme_text_color="Custom",
                        text_color="orange" if ingredient.amount < amount else "green",
                    ),
                    MDIconButton(
                        icon="dots-vertical",
                        theme_icon_color="Custom",
                        icon_color="black",
                        theme_bg_color="Custom",
                        md_bg_color="white",
                        pos_hint={"center_x": 0.5, "center_y": 0.5},
                        on_release=lambda x, d=menu_drink, i=ingredient_data: self.ingredient_drink_menu(x, d, i),
                    ),
                    theme_bg_color="Custom",
                    md_bg_color=TOP_APP_BAR_COLOR,
                )
                content_list.add_widget(ingredient_item)

        # Кнопка добавления ингредиента
        add_button = MDListItem(
            MDListItemLeadingIcon(
                icon="plus-circle",
            ),
            MDListItemHeadlineText(
                text="Добавить ингредиент",
                theme_text_color="Custom",
                text_color="black",
            ),
            MDListItemSupportingText(
                text="Нажмите чтобы добавить",
                theme_text_color="Custom",
                text_color="gray",
            ),
            theme_bg_color="Custom",
            md_bg_color="pink",
            on_release=lambda x, d=menu_drink: self.show_add_ingredient_to_drink_dialog(d),
        )
        content_list.add_widget(add_button)

        scroll = MDScrollView()
        scroll.add_widget(content_list)

        self.content_panel.add_widget(scroll)

    def ingredient_drink_menu(self, button, menu_drink, ingredient_data):
        """Меню для ингредиента в составе напитка"""
        menu_items = [
            {
                "text": "Изменить количество",
                "leading_icon": "counter",
                "on_release": lambda x=None, d=menu_drink, i=ingredient_data: self.edit_ingredient_amount_dialog(d, i),
            },
            {
                "text": "Удалить из состава",
                "leading_icon": "trash-can-outline",
                "on_release": lambda x=None, d=menu_drink, i=ingredient_data: self.remove_ingredient_from_drink(d, i),
            },
        ]

        self.ingredient_dropdown_menu = MDDropdownMenu(items=menu_items)
        self.ingredient_dropdown_menu.caller = button
        self.ingredient_dropdown_menu.open()

    def show_add_ingredient_to_drink_dialog(self, menu_drink):
        """Диалог добавления ингредиента в напиток"""
        self.fab_menu.dismiss() if hasattr(self, 'fab_menu') else None

        # Поле поиска ингредиентов
        search_field = MDTextField(
            MDTextFieldHintText(
                text="Поиск ингредиентов...",
                theme_text_color="Custom",
                text_color="gray"
            ),
            mode="outlined",
        )

        # Список ингредиентов для выбора
        ingredients_list = MDList(
            spacing=5,
            padding=5,
            size_hint_y=None,
        )
        ingredients_list.bind(minimum_height=ingredients_list.setter('height'))

        # Загружаем все ингредиенты
        all_ingredients = Ingredient.get_all()

        for ingredient in all_ingredients:
            # Проверяем, есть ли уже такой ингредиент в напитке
            existing = next((i for i in menu_drink.ingredients if i['ingredient'].id == ingredient.id), None)

            if not existing:
                ingredient_item = MDListItem(
                    MDListItemLeadingIcon(icon="water"),
                    MDListItemHeadlineText(
                        text=ingredient.name,
                        theme_text_color="Custom",
                        text_color="black",
                    ),
                    MDListItemSupportingText(
                        text=f"Остаток: {ingredient.amount} мл",
                        theme_text_color="Custom",
                        text_color="gray",
                    ),
                    theme_bg_color="Custom",
                    md_bg_color=TOP_APP_BAR_COLOR,
                    on_release=lambda x, d=menu_drink, i=ingredient: self.show_ingredient_amount_dialog(d, i),
                )
                ingredients_list.add_widget(ingredient_item)

        scroll = MDScrollView(
            size_hint_y=None,
            height=dp(300),
        )
        scroll.add_widget(ingredients_list)

        # Контейнер для контента
        content = MDBoxLayout(
            orientation="vertical",
            spacing=15,
            size_hint_y=None,
            height=dp(400),
        )
        content.add_widget(search_field)
        content.add_widget(scroll)

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Добавить ингредиент",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogContentContainer(
                content,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Закрыть", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
            ),
            size_hint=(0.9, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )

        # Функция поиска
        def filter_ingredients(instance, value):
            ingredients_list.clear_widgets()
            search_text = value.lower()

            for ingredient in all_ingredients:
                existing = next((i for i in menu_drink.ingredients if i['ingredient'].id == ingredient.id), None)

                if not existing and (not search_text or search_text in ingredient.name.lower()):
                    ingredient_item = MDListItem(
                        MDListItemLeadingIcon(icon="water"),
                        MDListItemHeadlineText(
                            text=ingredient.name,
                            theme_text_color="Custom",
                            text_color="black",
                        ),
                        MDListItemSupportingText(
                            text=f"Остаток: {ingredient.amount} мл",
                            theme_text_color="Custom",
                            text_color="gray",
                        ),
                        theme_bg_color="Custom",
                        md_bg_color=TOP_APP_BAR_COLOR,
                        on_release=lambda x, d=menu_drink, i=ingredient: self.show_ingredient_amount_dialog(d, i,
                                                                                                            dialog),
                    )
                    ingredients_list.add_widget(ingredient_item)

        search_field.bind(text=filter_ingredients)

        dialog.open()

    def show_ingredient_amount_dialog(self, menu_drink, ingredient, parent_dialog=None):
        """Диалог ввода количества ингредиента"""
        if parent_dialog:
            parent_dialog.dismiss()

        amount_input = MDTextField(
            MDTextFieldHintText(
                text="Количество, мл",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDTextFieldHelperText(
                text=f"Доступно: {ingredient.amount} мл",
                mode="persistent",
            ),
            mode="outlined",
            input_filter="int",
        )

        dialog = MDDialog(
            MDDialogHeadlineText(
                text=f"Добавить {ingredient.name}",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogSupportingText(
                text="Введите количество в мл",
                theme_text_color="Custom",
                text_color="grey"
            ),
            MDDialogContentContainer(
                amount_input,
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
                    on_release=lambda x: self.add_ingredient_to_drink(dialog, menu_drink, ingredient, amount_input)
                ),
            ),
            size_hint=(0.8, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def add_ingredient_to_drink(self, dialog, menu_drink, ingredient, amount_input):
        """Добавить ингредиент в напиток"""
        amount = amount_input.text.strip()

        if amount:
            try:
                amount_int = int(amount)

                if amount_int <= 0:
                    raise ValueError("Количество должно быть положительным")

                # Добавляем ингредиент в напиток
                menu_drink.add_ingredient(ingredient, amount_int)

                dialog.dismiss()

                # Обновляем экран
                self.show_drink_menu(menu_drink)

                MDSnackbar(
                    MDSnackbarText(
                        text=f"{ingredient.name} добавлен в {menu_drink.name}",
                        theme_text_color="Custom",
                        text_color="black"
                    ),
                    duration=1,
                ).open()

            except ValueError as e:
                amount_input.error = True
                MDSnackbar(
                    MDSnackbarText(
                        text=str(e) if str(e) else "Введите корректное количество",
                        theme_text_color="Custom",
                        text_color="black"
                    ),
                    duration=1,
                ).open()
        else:
            amount_input.error = True

    def edit_ingredient_amount_dialog(self, menu_drink, ingredient_data):
        """Диалог изменения количества ингредиента"""
        self.ingredient_dropdown_menu.dismiss()

        ingredient = ingredient_data['ingredient']
        current_amount = ingredient_data['amount']

        amount_input = MDTextField(
            MDTextFieldHintText(
                text="Новое количество, мл",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDTextFieldHelperText(
                text=f"Текущее: {current_amount} мл | Доступно: {ingredient.amount} мл",
                mode="persistent",
            ),
            mode="outlined",
            input_filter="int",
            text=str(current_amount),
        )

        dialog = MDDialog(
            MDDialogHeadlineText(
                text=f"Изменить {ingredient.name}",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogContentContainer(
                amount_input,
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
                    MDButtonText(text="Сохранить", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: self.update_ingredient_amount(dialog, menu_drink, ingredient_data,
                                                                       amount_input)
                ),
            ),
            size_hint=(0.8, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def update_ingredient_amount(self, dialog, menu_drink, ingredient_data, amount_input):
        """Обновить количество ингредиента"""
        amount = amount_input.text.strip()

        if amount:
            try:
                amount_int = int(amount)

                if amount_int <= 0:
                    raise ValueError("Количество должно быть положительным")

                # Обновляем количество
                ingredient_data['amount'] = amount_int

                dialog.dismiss()

                # Обновляем экран
                self.show_drink_menu(menu_drink)

                MDSnackbar(
                    MDSnackbarText(
                        text=f"Количество обновлено",
                        theme_text_color="Custom",
                        text_color="black"
                    ),
                    duration=1,
                ).open()

            except ValueError as e:
                amount_input.error = True
                MDSnackbar(
                    MDSnackbarText(
                        text=str(e) if str(e) else "Введите корректное количество",
                        theme_text_color="Custom",
                        text_color="black"
                    ),
                    duration=1,
                ).open()
        else:
            amount_input.error = True

    def remove_ingredient_from_drink(self, menu_drink, ingredient_data):
        """Удалить ингредиент из напитка"""
        self.ingredient_dropdown_menu.dismiss()

        ingredient = ingredient_data['ingredient']

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Удалить ингредиент?",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogSupportingText(
                text=f"Убрать {ingredient.name} из {menu_drink.name}?",
                theme_text_color="Custom",
                text_color="grey"
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Отмена", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="Удалить", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: self.process_remove_ingredient(dialog, menu_drink, ingredient_data)
                ),
            ),
            size_hint=(0.8, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def process_remove_ingredient(self, dialog, menu_drink, ingredient_data):
        """Обработать удаление ингредиента"""
        ingredient = ingredient_data['ingredient']

        # Удаляем ингредиент из напитка
        menu_drink.ingredients.remove(ingredient_data)

        dialog.dismiss()

        # Обновляем экран
        self.show_drink_menu(menu_drink)

        MDSnackbar(
            MDSnackbarText(
                text=f"{ingredient.name} удален из состава",
                theme_text_color="Custom",
                text_color="black"
            ),
            duration=1,
        ).open()

    def show_category_drinks(self, category):
        self.current_menu = "Напитки"

        self.add_back_button()
        self.top_app_bar_title.text = "Напитки"

        self.content_panel.clear_widgets()

        content_list = MDList(
            spacing=10,
            padding=10,
        )

        app = MDApp.get_running_app()
        menu_drinks = sorted([p for p in app.menu.menu_drinks if p.category_id == category.category_id],
                             key=lambda x: x.name)

        if not menu_drinks:
            empty_item = MDListItem(
                MDListItemLeadingIcon(icon="account-off"),
                MDListItemHeadlineText(
                    text="Напитки отсутствуют!",
                    theme_text_color="Custom",
                    text_color="black",
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
            )
            content_list.add_widget(empty_item)
            return

        for menu_drink in menu_drinks:
            length = len(menu_drink.drinks)
            drinks = sorted(menu_drink.drinks, key=lambda x: x.size)

            main_text = f"{menu_drink.name}     {drinks[0].price} | {drinks[1].price} BYN" \
                if length > 1 else f"{menu_drink.name}     {drinks[0].price} BYN"

            support_text = f"{drinks[0].size} | {drinks[1].size} {drinks[0].size_unit}" \
                if length > 1 else f"{drinks[0].size} {drinks[0].size_unit}"

            product_item = MDListItem(
                MDListItemLeadingIcon(
                    icon="account",
                ),
                MDListItemHeadlineText(
                    text=main_text,
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDListItemSupportingText(
                    text=support_text,
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
                on_release=lambda x, d=menu_drink: self.show_drink_menu(d),
            )
            content_list.add_widget(product_item)

        scroll = MDScrollView()
        scroll.add_widget(content_list)

        self.content_panel.add_widget(scroll)

    def show_menu(self):
        self.current_menu = "Категории"

        self.add_back_button()
        self.top_app_bar_title.text = "Категории"

        self.content_panel.clear_widgets()

        content_list = MDList(
            spacing=10,
            padding=10,
        )

        app = MDApp.get_running_app()
        categories = app.menu.categories

        if not categories:
            empty_item = MDListItem(
                MDListItemLeadingIcon(icon="account-off"),
                MDListItemHeadlineText(
                    text="Категории отсутствуют!",
                    theme_text_color="Custom",
                    text_color="black",
                ),
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
            )
            content_list.add_widget(empty_item)
            return

        for category in categories:
            category_item = MDListItem(
                MDListItemLeadingIcon(
                    icon="account",
                ),
                MDListItemHeadlineText(
                    text=category.name,
                    theme_text_color="Custom",
                    text_color="black",
                ),
                MDListItemSupportingText(
                    text="Десерты" if category.name == "Десерты" else "Добавки" if category.name == "Добавки" else "Напитки",
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
                on_release=lambda x, c=category: self.show_category_drinks(c),
            )
            content_list.add_widget(category_item)

        scroll = MDScrollView()
        scroll.add_widget(content_list)

        self.content_panel.add_widget(scroll)

    def show_ingredients(self):
        self.current_menu = "Ингредиенты"

        self.add_back_button()
        self.top_app_bar_title.text = "Ингредиенты"

        self.content_panel.clear_widgets()

        content_list = MDList(
            spacing=10,
            padding=10,
        )

        # Получаем общее количество ингредиентов для отображения в помощнике
        total_ingredients = len(Ingredient.get_all())

        # Поле ввода поиска
        self.search_input = MDTextField(
            MDTextFieldHintText(
                text="Поиск ингредиентов...",
                theme_text_color="Custom",
                text_color="gray"
            ),
            MDTextFieldHelperText(
                text=f"Всего: {total_ingredients}",  # Изначально показываем общее количество
                mode="persistent",
                theme_text_color="Custom",
                text_color="gray",
            ),
            mode="outlined",
            size_hint_y=None,
            height=40,
        )
        self.search_input.bind(text=self.on_search_text_changed)

        box = MDBoxLayout(
            padding=10,
            size_hint_y=None,
            height=60,
        )

        box.add_widget(self.search_input)
        self.content_panel.add_widget(box)

        # Добавляем список ингредиентов
        self.ingredients_content_list = content_list
        scroll = MDScrollView()
        scroll.add_widget(content_list)

        self.content_panel.add_widget(scroll)

        self.load_ingredients_list()

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
        self.show_fab_menu()

    def show_add_category_dialog(self):
        pass

    def show_add_product_dialog(self):
        pass

    def show_fab_menu(self):
        if self.current_menu == "Меню":
            menu_items = [
                {
                    "text": "Добавить категорию",
                    "leading_icon": "account-plus",
                    "on_release": self.show_add_category_dialog
                },
            ]
        elif self.current_menu == "Напитки":
            menu_items = [
                {
                    "text": "Добавить Напиток",
                    "leading_icon": "account-plus",
                    "on_release": self.show_add_product_dialog
                },
            ]
        elif self.current_menu == "Бариста":
            menu_items = [
                {
                    "text": "Добавить бариста",
                    "leading_icon": "account-plus",
                    "on_release": self.show_add_barista_dialog
                },
            ]
        elif self.current_menu == "Финансы":
            menu_items = [
                {
                    "text": "Добавить расходы",
                    "leading_icon": "cash-plus",
                    "on_release": self.show_add_finance_dialog
                },
            ]
        elif self.current_menu == "Ингредиенты":
            menu_items = [
                {
                    "text": "Добавить ингредиент",
                    "leading_icon": "water-plus",
                    "on_release": self.show_add_ingredient_dialog
                },
            ]
        else:
            menu_items = []

        self.fab_menu = MDDropdownMenu(
            items=menu_items,
            caller=self.fab_button,
        )
        self.fab_menu.open()

    def show_add_barista_dialog(self):
        self.fab_menu.dismiss()

        self.barista_name_input = MDTextField(
            MDTextFieldHintText(
                text="Имя",
                theme_text_color="Custom",
                text_color="black"
            ),
            mode="outlined"
        )

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Добавить бариста?",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogSupportingText(
                text="Введите имя",
                theme_text_color="Custom",
                text_color="grey"
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
            dialog.dismiss()

            Barista.create(name=name)
            self.show_baristas()

            MDSnackbar(
                MDSnackbarText(text=f"Бариста '{name}' добавлен успешно!", theme_text_color="Custom",
                               text_color="black"),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.7,
                theme_bg_color="Primary",
                radius=[10, 10, 10, 10],
                duration=1,
            ).open()
        else:
            self.barista_name_input.error = True

    def show_add_finance_dialog(self):
        self.fab_menu.dismiss()

        self.finance_description = MDTextField(
            MDTextFieldHintText(
                text="Название",
                theme_text_color="Custom",
                text_color="black"
            ),
            mode="outlined",
        )

        self.finance_amount = MDTextField(
            MDTextFieldHintText(
                text="Сумма, BYN",
                theme_text_color="Custom",
                text_color="black"
            ),
            mode="outlined",
            input_filter="float",
        )

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Добавить расходы?",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogSupportingText(
                text="Введите название и сумму",
                theme_text_color="Custom",
                text_color="grey"
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

    def add_new_finance(self, dialog):
        description = self.finance_description.text.strip()
        amount = self.finance_amount.text.strip()

        if description and amount:
            try:
                summ = float(amount)

                dialog.dismiss()
                self.show_finance()

                MDSnackbar(
                    MDSnackbarText(
                        text=f"Операция '{description}' добавлена успешно!",
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
                MDSnackbar(
                    MDSnackbarText(
                        text=f"Сумма введена некорректно!",
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
        else:
            if not description:
                self.finance_description.error = True

            if not amount:
                self.finance_amount.error = True

    def show_add_ingredient_dialog(self):
        self.fab_menu.dismiss()

        self.ingredient_name = MDTextField(
            MDTextFieldHintText(
                text="Название",
                theme_text_color="Custom",
                text_color="black"
            ),
            mode="outlined",
        )

        self.ingredient_volume = MDTextField(
            MDTextFieldHintText(
                text="Объем, шт/мл/г",
                theme_text_color="Custom",
                text_color="black"
            ),
            mode="outlined",
            input_filter="int",
        )

        self.ingredient_price = MDTextField(
            MDTextFieldHintText(
                text="Цена, BYN",
                theme_text_color="Custom",
                text_color="black"
            ),
            mode="outlined",
            input_filter="float",
        )

        self.ingredient_calories = MDTextField(
            MDTextFieldHintText(
                text="Калории, Ккал/100 мл/г",
                theme_text_color="Custom",
                text_color="black"
            ),
            mode="outlined",
            input_filter="int",
        )

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Добавить ингредиент?",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogSupportingText(
                text="Введите название, объем, цену и калории",
                theme_text_color="Custom",
                text_color="grey"
            ),
            MDDialogContentContainer(
                self.ingredient_name,
                self.ingredient_volume,
                self.ingredient_price,
                self.ingredient_calories,
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
        name = self.ingredient_name.text.strip()
        volume = self.ingredient_volume.text.strip()
        price = self.ingredient_price.text.strip()
        calories = self.ingredient_calories.text.strip()

        if name and volume and price:
            try:
                volume_int = int(volume)
                price_float = float(price)
                calories_int = int(calories) if calories else 0

                dialog.dismiss()

                # ОБНОВЛЯЕМ СПИСОК, а не пересоздаем экран!
                self.refresh_ingredients_list()

                # Очищаем поле поиска
                if hasattr(self, 'search_input'):
                    self.search_input.text = ""

                MDSnackbar(
                    MDSnackbarText(
                        text=f"Ингредиент '{name}' добавлен успешно!",
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
                MDSnackbar(
                    MDSnackbarText(
                        text=f"Объем или цена указана некорректно!",
                        theme_text_color="Custom",
                        text_color="black"
                    ),
                    duration=1,
                ).open()
        else:
            if not name:
                self.ingredient_name.error = True
            if not volume:
                self.ingredient_volume.error = True
            if not price:
                self.ingredient_price.error = True

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
