import asyncio
import os

from kivy.metrics import dp
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivymd.uix.appbar import MDTopAppBarTrailingButtonContainer, MDActionTopAppBarButton, MDTopAppBarTitle, \
    MDTopAppBarLeadingButtonContainer, MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton, MDButtonIcon
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialogButtonContainer, MDDialogHeadlineText, MDDialog, MDDialogSupportingText, \
    MDDialogContentContainer
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItemHeadlineText, MDListItem, MDList, MDListItemSupportingText, \
    MDListItemTertiaryText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.segmentedbutton import MDSegmentedButton, MDSegmentedButtonItem, MDSegmentButtonLabel
from kivymd.uix.selectioncontrol import MDCheckbox, MDSwitch
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.widget import MDWidget

from headers import Order, Barista, TOP_APP_BAR_COLOR, Category, Drink, MenuDrink


class MainMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main_menu"
        self.md_bg_color = "whitesmoke"

        self.top_app_bar = None
        self.toolbar_menu = None

        self.categories_panel = None
        self.categories_list = None

        self.menu_drinks_panel = None
        self.menu_drinks_label = None
        self.menu_drink_card_quantity_labels = {}
        self.menu_drinks_list = None
        self.cart_button = None
        self.cart_list = None

        app = MDApp.get_running_app()
        self.selected_category = app.menu.categories[0]
        self.barista = None

        self.scroll_view = None
        self.cart_total_value_label = None

        self.order_menu = None
        self.order_list = None
        self.order_total_value = None

        self.shift_menu = None
        self.shift_list = None
        self.shift_total_value = None

        self.build_ui()

    def snack_bar(self, text):
        MDSnackbar(
            MDSnackbarText(text=text, theme_text_color="Custom", text_color="black"),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
            theme_bg_color="Primary",
            radius=[10, 10, 10, 10],
            duration=1,
        ).open()

    def update_for_barista(self, barista: Barista):
        self.barista = barista

        if hasattr(self, 'top_app_bar'):
            child = self.top_app_bar.children[1].children[1].children[0]
            if isinstance(child, MDTopAppBarTitle):
                child.text = f"Бариста {self.barista.name}"

    def toolbar_menu_init(self):
        menu_items = [
            {
                "text": "Заказы",
                "leading_icon": "history",
                "on_release": self.show_order_history,
            },
            {
                "text": "Смены",
                "leading_icon": "clock-time-three",
                "on_release": self.show_shifts,
            },
        ]

        self.toolbar_menu = MDDropdownMenu(
            items=menu_items,
            # theme_bg_color="Custom",
            # md_bg_color=TOP_APP_BAR_COLOR
        )

    def toolbar_menu_open(self, button):
        self.toolbar_menu.caller = button
        self.toolbar_menu.open()

    def top_app_bar_init(self):
        app = MDApp.get_running_app()
        if app.shift:
            self.barista = app.shift.barista

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
                text=f"Бариста {self.barista.name if self.barista else 'Бариста'}",
                theme_text_color="Custom",
                text_color="black",
                pos_hint={"center_x": .5},
            ),
            MDTopAppBarTrailingButtonContainer(
                MDActionTopAppBarButton(
                    icon="logout-variant",
                    theme_text_color="Custom",
                    text_color="black",
                    on_release=self.show_close_shift_dialog,
                )
            ),
            theme_bg_color="Custom",
            md_bg_color=TOP_APP_BAR_COLOR
        )

        self.toolbar_menu_init()

    def categories_panel_list_update(self):
        for child in self.categories_list.children:
            if isinstance(child, MDListItem):
                child.md_bg_color = "pink" if child.id == self.selected_category.name else TOP_APP_BAR_COLOR

    def categories_panel_init(self):
        self.categories_panel = MDBoxLayout(
            orientation="vertical",
            size_hint=(0.3, 1.0),
            padding=[10, 10, 10, 5],
            # spacing=5,
            radius=[10, 10, 10, 10],
            # pos_hint={"center_x": 0.5, "center_y": 0.5},
            theme_bg_color="Custom",
            md_bg_color=TOP_APP_BAR_COLOR
        )

        categories_label = MDLabel(
            text="Категории",
            halign="left",
            theme_text_color="Custom",
            text_color="black",
            adaptive_height=True,
            font_style="Title",
            role="medium",
            bold=True
        )

        self.categories_list = MDList(spacing=0)

        scroll_view_categories_list = MDScrollView()
        scroll_view_categories_list.add_widget(self.categories_list)

        self.categories_panel.add_widget(categories_label)
        # self.categories_panel.add_widget(
        #     MDDivider(
        #         theme_divider_color="Custom",
        #         color=SECONDARY_COLOR
        #     )
        # )
        self.categories_panel.add_widget(scroll_view_categories_list)

        app = MDApp.get_running_app()

        for category in app.menu.categories:
            item = MDListItem(
                # MDListItemLeadingIcon(icon=category["icon"]),
                MDListItemHeadlineText(
                    text=category.name,
                    theme_text_color="Custom",
                    text_color="black",
                    font_style="Title",
                    role="small",
                    bold=False,
                ),
                id=category.name,
                divider=True,
                divider_color="black",
                theme_bg_color="Custom",
                md_bg_color="pink" if category == self.selected_category else TOP_APP_BAR_COLOR,
                on_release=lambda x, cat=category: self.select_category(cat),
                size_hint_y=None,
                height="50dp",
                radius=[5, 5, 5, 5]
            )

            self.categories_list.add_widget(item)
            # self.categories_list.add_widget(
            #     MDDivider(
            #         theme_bg_color="Custom",
            #         color="black"
            #     )
            # )

    def menu_drinks_panel_list_update(self):
        app = MDApp.get_running_app()

        self.menu_drinks_list.clear_widgets()
        self.menu_drinks_list.parent.scroll_y = 1.0

        menu_drinks = sorted([p for p in app.menu.menu_drinks if p.category_id == self.selected_category.category_id],
                          key=lambda x: x.name)

        for menu_drink in menu_drinks:
            card = MDCard(
                orientation="vertical",
                size_hint=(1, None),
                height=dp(120),
                padding=[dp(10), dp(5), dp(10), dp(5)],
                spacing=dp(10),
                radius=[dp(10), dp(10), dp(10), dp(10)],
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                style="elevated",
                theme_elevation_level="Custom",
                elevation_level=1,
                pos_hint={"center_y": 0.6}
            )

            card_layout = MDRelativeLayout()
            card.add_widget(card_layout)
            #
            # # Добавь картинку в начало card_layout
            # menu_drink_image = FitImage(
            #     source=f"assets/images/cappuccino.jpg",
            #     # size_hint=(None, 1.0),
            #     # height=100,
            #     radius=[10, 10, 10, 10],
            #     pos_hint={"center_x": 0.5, "center_y": 0.1}
            # )
            # card_layout.add_widget(menu_drink_image)

            # Верхняя строка: название и цена
            top_row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(30),
                pos_hint={"center_y": 0.6}
            )

            # Название продукта
            menu_drink_name_label = MDLabel(
                text=f"{menu_drink.name} {menu_drink.selected_drink.size} {menu_drink.selected_drink.size_unit}",
                halign="left",
                font_style="Title",
                role="medium",
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.7,
            )

            price_label = MDLabel(
                text=f"{menu_drink.selected_drink.price} BYN",
                halign="right",
                padding=10,
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.3,
                bold=True
            )

            top_row.add_widget(menu_drink_name_label)
            top_row.add_widget(price_label)
            card_layout.add_widget(top_row)

            # Нижняя строка: выбор размера (если есть) и кнопки
            bottom_row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(40),
                spacing=dp(40)
            )

            # Контейнер для кнопок размеров
            size_container = MDBoxLayout(
                orientation="horizontal",
                spacing=5,
                padding=10,
                size_hint_x=0.6,
            )

            drink_amount = len(menu_drink.drinks)
            if drink_amount > 1:
                size_button = MDSegmentedButton(
                    type="small",
                )

                drinks = sorted(menu_drink.drinks, key=lambda x: x.size)
                for drink in drinks:
                    size_button.add_widget(
                        MDSegmentedButtonItem(
                            MDSegmentButtonLabel(
                                text=f"{drink.size}",
                                # theme_text_color="Custom",
                                # text_color="black",
                                theme_font_size="Custom",
                                font_size="15sp",
                            ),
                            active=drink == drinks[0],
                            selected_color="pink",
                            on_release=lambda x, p=menu_drink, d=drink: self.select_drink(x, p, d)
                        )
                    )

                size_container.add_widget(size_button)

            bottom_row.add_widget(size_container)

            # Кнопки добавления/удаления
            buttons_container = MDBoxLayout(
                orientation="horizontal",
                padding=[0, 0, 0, 5],
                size_hint_x=0.4
            )

            # Кнопка уменьшения количества
            pop_button = MDIconButton(
                icon="minus",
                theme_text_color="Custom",
                text_color="black",
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                theme_font_size="Custom",
                font_size="16sp",
            )
            pop_button.bind(on_release=lambda x, d=menu_drink: self.pop_from_cart(menu_drink=d))

            menu_drink_amount = sum(
                item.quantity for item in app.cart.cart_items if item.drink.drink_id == menu_drink.drink_id)

            # Поле для отображения количества в корзине
            quantity_label = MDLabel(
                text=str(menu_drink_amount),
                theme_text_color="Custom",
                text_color="black",
                halign="center",
                valign="center",
                size_hint_y=1.0,
            )

            self.menu_drink_card_quantity_labels[menu_drink.name] = quantity_label

            # Кнопка увеличения количества
            add_button = MDIconButton(
                icon="plus",
                theme_text_color="Custom",
                text_color="black",
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                theme_font_size="Custom",
                font_size="16sp",
                size_hint=(None, None),
                size=("50dp", "50dp"),
            )
            add_button.bind(on_release=lambda x, d=menu_drink: self.add_to_cart(menu_drink=d))

            buttons_container.add_widget(pop_button)
            buttons_container.add_widget(quantity_label)
            buttons_container.add_widget(add_button)

            bottom_row.add_widget(buttons_container)
            card.add_widget(bottom_row)

            card_container = MDBoxLayout(
                orientation="vertical",
                padding=[5, 0, 0, 0],
                size_hint=(1, None),
                height=dp(120),
            )

            card_container.add_widget(card)

            self.menu_drinks_list.add_widget(card_container)

    def menu_drinks_panel_init(self):
        self.menu_drinks_panel = MDBoxLayout(
            orientation="vertical",
            size_hint=(0.7, 1.0),
            padding=[10, 10, 5, 5],
            spacing=10,
            radius=[10, 10, 10, 10],
            # pos_hint={"center_x": 0.5, "center_y": 0.5},
            theme_bg_color="Custom",
            md_bg_color=TOP_APP_BAR_COLOR
        )

        self.menu_drinks_label = MDLabel(
            text="Кофе",
            halign="left",
            theme_text_color="Custom",
            text_color="black",
            adaptive_height=True,
            font_style="Title",
            role="medium",
            bold=True
        )

        self.menu_drinks_list = MDList(
            spacing=10,
            padding=5,
            size_hint=(0.95, 1),
            # pos_hint={"center_x": 0.5, "center_y": 0.5},
            # theme_bg_color="Custom",
            # md_bg_color=FOURTH_COLOR
        )

        self.cart_button = MDButton(
            MDButtonIcon(
                icon="cart",
                halign="left",
                # pos_hint={"center_x": 0.42, "center_y": 0.5},
                theme_text_color="Custom",
                text_color="black"),
            MDButtonText(
                id="text",
                text="0 BYN",
                halign="right",
                theme_text_color="Custom",
                text_color="black",
                adaptive_size=True,
                # pos_hint={"center_x": 0.58, "center_y": 0.5}
            ),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color="pink",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            height="50dp",
            theme_width="Custom",
            # size_hint=(0.5, 0.8),
            size_hint_x=None,
            width=120,
            on_release=self.show_cart
        )

        menu_drinks_scroll = MDScrollView()
        menu_drinks_scroll.add_widget(self.menu_drinks_list)

        self.menu_drinks_panel.add_widget(self.menu_drinks_label)
        # self.menu_drinks_panel.add_widget(
        #     MDDivider(
        #         theme_divider_color="Custom",
        #         color=SECONDARY_COLOR
        #     )
        # )
        self.menu_drinks_panel.add_widget(menu_drinks_scroll)
        self.menu_drinks_panel.add_widget(self.cart_button)

        self.menu_drinks_panel_list_update()

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
        self.categories_panel_init()
        self.menu_drinks_panel_init()

        content_layout.add_widget(self.categories_panel)
        content_layout.add_widget(self.menu_drinks_panel)

        main_layout.add_widget(self.top_app_bar)
        main_layout.add_widget(content_layout)

        self.add_widget(main_layout)

    def select_category(self, category: Category):
        self.selected_category = category

        self.menu_drinks_label.text = self.selected_category.name

        self.categories_panel_list_update()
        self.menu_drinks_panel_list_update()

    def select_drink(self, button, menu_drink: MenuDrink, drink: Drink):
        menu_drink.selected_drink = drink

        button.parent.parent.parent.parent.parent.children[1].children[0].children[
            1].text = f"{menu_drink.name} {drink.size} {drink.size_unit}"
        button.parent.parent.parent.parent.parent.children[1].children[0].children[
            0].text = f"{drink.price} BYN"

    # Метод добавления в корзину
    def add_to_cart(self, menu_drink: MenuDrink = None, drink: Drink = None):
        app = MDApp.get_running_app()

        drink = menu_drink.selected_drink if menu_drink else drink

        if drink:
            app.cart.add_drink(drink)

            self.update_cart_counter()
            self.update_card_counter(drink.name)
            self.cart_items_update()

    # Метод удаления из корзины
    def pop_from_cart(self, menu_drink: MenuDrink = None, drink: Drink = None):
        app = MDApp.get_running_app()

        drink = menu_drink.selected_drink if menu_drink else drink

        if drink:
            app.cart.pop_drink(drink)

            self.update_cart_counter()
            self.update_card_counter(drink.name)
            self.cart_items_update()

    # Вспомогательный метод для форматирования отображения размера
    def format_size_display(self, size):
        if size == 1:
            return "1 шт"
        elif size < 1000:
            return f"{size} мл"
        else:
            if size % 1000 == 0:
                return f"{size // 1000}л"
            else:
                return f"{size / 1000:.1f}л"

    def update_card_counter(self, drink_name):
        app = MDApp.get_running_app()

        menu_drink_amount = sum(item.quantity for item in app.cart.cart_items if item.drink.name == drink_name)
        card_quantity_label = self.menu_drink_card_quantity_labels.get(drink_name)
        if card_quantity_label and isinstance(card_quantity_label, MDLabel):
            card_quantity_label.text = str(menu_drink_amount)

    def reset_card_counter(self):
        for val in self.menu_drink_card_quantity_labels.values():
            val.text = "0"

    def update_cart_counter(self):
        app = MDApp.get_running_app()

        for child in self.cart_button.children:
            if isinstance(child, MDButtonText):
                child.text = f"{app.cart.total_price:.2f} BYN"
                break

    def update_cart_total_value(self):
        app = MDApp.get_running_app()

        self.cart_total_value_label.text = f"{app.cart.total_price:.2f} BYN"

    def cart_items_update(self):
        app = MDApp.get_running_app()

        if not isinstance(self.scroll_view, MDScrollView):
            return

        self.scroll_view.clear_widgets()

        if len(app.cart.cart_items) < 5:
            self.scroll_view.scroll_y = 1.0

        cart_content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        cart_content.bind(minimum_height=cart_content.setter('height'))

        for i, cart_item in enumerate(sorted(app.cart.cart_items, key=lambda x: x.drink.name)):
            item_layout = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(50),
                spacing=5,
                padding=5,
            )

            item_info = MDLabel(
                valign="bottom",
                text=f"{cart_item.drink.name} {cart_item.drink.size} {cart_item.drink.size_unit} x {cart_item.quantity}",
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.5
            )

            item_total = MDLabel(
                valign="bottom",
                halign="center",
                text=f"{cart_item.total_price} BYN",
                theme_text_color="Custom",
                text_color="black",
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                size_hint_x=0.5
            )

            # Кнопки добавления/удаления
            buttons_container = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(5),
                padding=2,
                size_hint_x=0.3
            )

            # Кнопки добавления/удаления
            buttons_container = MDBoxLayout(
                orientation="horizontal",
                padding=[0, 0, 0, 5],
                size_hint_x=0.3
            )

            # Кнопка уменьшения количества
            pop_button = MDIconButton(
                icon="minus",
                theme_text_color="Custom",
                text_color="black",
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                theme_font_size="Custom",
                font_size="16sp",
            )
            pop_button.bind(on_release=lambda x, d=cart_item.drink: self.pop_from_cart(drink=d))

            item_amount = sum(
                item.quantity for item in app.cart.cart_items if item.drink.drink_id == cart_item.drink.drink_id)

            # Поле для отображения количества в корзине
            quantity_label = MDLabel(
                text=str(item_amount),
                theme_text_color="Custom",
                text_color="black",
                halign="center",
                valign="center",
                size_hint_y=1.0,
                bold=True
            )

            # Кнопка увеличения количества
            add_button = MDIconButton(
                icon="plus",
                theme_text_color="Custom",
                text_color="black",
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                theme_font_size="Custom",
                font_size="16sp",
            )
            add_button.bind(on_release=lambda x, d=cart_item.drink: self.add_to_cart(drink=d))

            buttons_container.add_widget(pop_button)
            buttons_container.add_widget(quantity_label)
            buttons_container.add_widget(add_button)

            item_layout.add_widget(item_info)
            item_layout.add_widget(item_total)
            item_layout.add_widget(buttons_container)

            cart_content.add_widget(item_layout)

        self.update_cart_total_value()

        self.scroll_view.add_widget(cart_content)

    def show_cart(self, *args):
        app = MDApp.get_running_app()

        if not app.cart.cart_items:
            self.snack_bar("Корзина пуста")
            return

        total_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            spacing=5,
            padding=[5, 5, 15, 5],
        )

        total_label = MDLabel(
            text="Итого:",
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(20),
            bold=True,
            size_hint_x=0.5
        )

        self.cart_total_value_label = MDLabel(
            text="0 BYN",
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(20),
            bold=True,
            halign="right",
            size_hint_x=0.5
        )

        total_layout.add_widget(total_label)
        total_layout.add_widget(self.cart_total_value_label)

        self.scroll_view = MDScrollView(
            size_hint=(1, None),
            height=dp(200)
        )

        self.cart_items_update()

        # Создаем контейнер для выбора скидки
        discount_container = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            spacing=5,
            padding=[5, 5, 5, 5],
        )

        discount_label = MDLabel(
            text="Укажите скидку:",
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(16),
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        discount_container.add_widget(discount_label)

        # ОПРЕДЕЛЯЕМ ФУНКЦИИ ПЕРВЫМИ!
        def update_price():
            if switch_10.active:
                discount = 10
            elif switch_30.active:
                discount = 30
            elif switch_50.active:
                discount = 50
            else:
                discount = 0

            app.cart.discount = discount

            self.update_cart_counter()
            self.update_cart_total_value()

        def on_switch_activate(active_switch, value):
            if value:
                if active_switch != switch_10:
                    switch_10.active = False
                if active_switch != switch_30:
                    switch_30.active = False
                if active_switch != switch_50:
                    switch_50.active = False

            update_price()

        # ТЕПЕРЬ СОЗДАЕМ SWITCH С ACTIVE ПРИ СОЗДАНИИ
        # Строка с MDSwitch для скидки 10%
        row_10 = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(32),
        )
        row_10.add_widget(MDLabel(text="Скидка 10%"))
        switch_10 = MDSwitch(
            thumb_color_active="pink",
            thumb_color_inactive="grey",
            track_color_active="lightgrey",
            track_color_inactive="white",
            on_active=lambda x, y: on_switch_activate(switch_10, y)
        )
        row_10.add_widget(switch_10)
        discount_container.add_widget(row_10)

        # Строка с MDSwitch для скидки 30%
        row_30 = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(32),
        )
        row_30.add_widget(MDLabel(text="Скидка 30%"))
        switch_30 = MDSwitch(
            thumb_color_active="pink",
            thumb_color_inactive="grey",
            track_color_active="lightgrey",
            track_color_inactive="white",
            on_active=lambda x, y: on_switch_activate(switch_30, y)
        )
        row_30.add_widget(switch_30)
        discount_container.add_widget(row_30)

        # Строка с MDSwitch для скидки 50%
        row_50 = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(32),
        )
        row_50.add_widget(MDLabel(text="Скидка 50%"))
        switch_50 = MDSwitch(
            thumb_color_active="pink",
            thumb_color_inactive="grey",
            track_color_active="lightgrey",
            track_color_inactive="white",
            on_active=lambda x, y: on_switch_activate(switch_50, y)
        )
        row_50.add_widget(switch_50)
        discount_container.add_widget(row_50)

        # Устанавливаем начальную цену
        self.cart_total_value_label.text = f"{app.cart.total_price:.2f} BYN"

        dialog = MDDialog(
            MDDialogHeadlineText(text="Корзина", theme_text_color="Custom", text_color="black"),
            MDDialogContentContainer(
                MDDivider(),
                self.scroll_view,
                MDDivider(),
                discount_container,
                total_layout,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Отмена", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDWidget(),
                MDButton(
                    MDButtonText(text="Баллами", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: self.create_order(dialog, True)
                ),
                MDWidget(),
                MDButton(
                    MDButtonText(text="На кассе", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: self.create_order(dialog)
                ),
            ),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )

        dialog.open()

        if app.cart.discount == 10:
            switch_10.active = True
        elif app.cart.discount == 30:
            switch_30.active = True
        elif app.cart.discount == 50:
            switch_50.active = True

    def create_order(self, dialog, is_free=False):
        app = MDApp.get_running_app()

        if not app.cart.cart_items:
            dialog.dismiss()
            return

        order = Order()
        for cart_item in app.cart.cart_items:
            order.add_item(cart_item)

        if is_free:
            self.show_free_confirmation(order)
        else:
            app.shift.add_order(order)
            self.show_order_confirmation(order)

        app.cart.clear()
        dialog.dismiss()

        self.update_cart_counter()
        self.reset_card_counter()

    def show_free_confirmation(self, order: Order):
        app = MDApp.get_running_app()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            qr_path = loop.run_until_complete(app.telegram_bot.qr.encode_free_order(order))
        finally:
            loop.close()

        if os.path.exists(qr_path):
            qr_image = Image(
                source=qr_path,
                size_hint_y=None,
                height=200,
            )
            qr_image.reload()
        else:
            from kivy.uix.label import Label
            qr_image = Label(
                text="QR-код\nнедоступен",
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=200
            )

        dialog = MDDialog(
            MDDialogHeadlineText(text="Заказ будет оформлен после подтверждения баланса!", theme_text_color="Custom", text_color="black"),
            MDDialogContentContainer(
                qr_image,
                MDDialogSupportingText(text=f"Итого: {order.total_price} PIG",
                                       theme_text_color="Custom", text_color="black"),
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="OK", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: dialog.dismiss()
                ),
            ),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def show_order_confirmation(self, order):
        app = MDApp.get_running_app()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            qr_path = loop.run_until_complete(app.telegram_bot.qr.encode_order(order))
        finally:
            loop.close()

        if os.path.exists(qr_path):
            qr_image = Image(
                source=qr_path,
                size_hint_y=None,
                height=200,
            )
            qr_image.reload()
        else:
            from kivy.uix.label import Label
            qr_image = Label(
                text="QR-код\nнедоступен",
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=200
            )

        dialog = MDDialog(
            MDDialogHeadlineText(text="Заказ успешно оформлен!", theme_text_color="Custom", text_color="black"),
            MDDialogContentContainer(
                qr_image,
                MDDialogSupportingText(text=f"Заказ №{order.order_id}\n"
                                            f"Время: {order.created_at}\n\n"
                                            f"Итого: {order.total_price} BYN",
                                       theme_text_color="Custom", text_color="black"),
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="OK", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: dialog.dismiss()
                ),
            ),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def show_shift_order_history(self, shift):
        shift.get_orders()
        self.show_order_history(shift)

    def order_list_update(self, shift_orders=None):
        self.order_list.clear_widgets()

        app = MDApp.get_running_app()
        orders = shift_orders or app.shift.orders

        for order in reversed(orders):
            order_list_item = MDListItem(
                MDListItemHeadlineText(
                    text=f"Заказ №{order.order_id}",
                    theme_text_color="Custom",
                    text_color="black",
                    font_style="Title",
                    role="medium",
                    bold=False
                ),
                MDListItemSupportingText(
                    text=order.created_at,
                    theme_text_color="Custom",
                    text_color="black",
                    font_style="Title",
                    role="small",
                    bold=False
                ),
                MDListItemTertiaryText(
                    text=f"{order.drink_amount}"
                         f" {'позиций' if order.drink_amount > 4 else 'позиции' if order.drink_amount > 1 else 'позиция'}"
                         f" на сумму {order.total_price} {'PIG' if order.is_free else 'BYN'}",
                    theme_text_color="Custom",
                    text_color="black",
                    font_style="Title",
                    role="small",
                    bold=False
                ),
                MDIconButton(
                    icon="dots-vertical",
                    theme_icon_color="Custom",
                    icon_color="black",
                    theme_bg_color="Custom",
                    md_bg_color="white",
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda x, o=order: self.show_order_menu(x, o)
                ),
                divider=True,
                divider_color="black",
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                on_release=lambda x, o=order: self.show_order_details(o)
            )

            self.order_list.add_widget(order_list_item)

    def order_list_total_value_update(self, shift_orders=None):
        self.order_total_value.clear_widgets()

        app = MDApp.get_running_app()
        orders = shift_orders or app.shift.orders

        total_label = MDLabel(
            text="Всего:",
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(20),
            size_hint_x=0.3
        )

        total_amount = len(orders)
        cart_total_amount_label = MDLabel(
            text=f"{total_amount} {'заказов' if total_amount > 4 else 'заказа' if total_amount > 1 else 'заказ'}",
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(20),
            bold=True,
            halign="right",
        )

        summ = 0
        points = 0
        for order in orders:
            if order.is_free:
                points += order.total_price
            else:
                summ += order.total_price

        cart_total_value_label = MDLabel(
            text=f"{summ} BYN + {points} PIG",
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(20),
            bold=True,
            halign="right",
        )

        self.order_total_value.add_widget(total_label)
        self.order_total_value.add_widget(cart_total_amount_label)
        self.order_total_value.add_widget(cart_total_value_label)

    def show_order_history(self, target_shift=None):
        self.toolbar_menu.dismiss()

        app = MDApp.get_running_app()

        shift = target_shift or app.shift
        shift.get_orders()
        orders = shift.orders

        if not orders:
            self.snack_bar("История заказов пуста")
            return

        header_box = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=5,
            padding=[5, 5, 5, 5],
        )

        order_id_label = MDLabel(
            text=f"Смена",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=dp(25)
        )

        time_label = MDLabel(
            text=f"{shift.start_time.strftime('%d.%m.%Y')}",
            halign="right",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=dp(25)
        )

        header_box.add_widget(order_id_label)
        header_box.add_widget(time_label)

        self.order_list = MDList()

        self.order_list_update(orders)

        order_list_scroll_view = MDScrollView(
            size_hint_y=None,
            height=dp(250)
        )

        order_list_scroll_view.add_widget(self.order_list)

        self.order_total_value = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            spacing=5,
            padding=[5, 5, 5, 5],
        )

        self.order_list_total_value_update(orders)

        order_history_dialog = MDDialog(
            MDDialogHeadlineText(text="История заказов", theme_text_color="Custom", text_color="black"),
            MDDialogContentContainer(
                header_box,
                MDDivider(),
                order_list_scroll_view,
                MDDivider(),
                self.order_total_value,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Закрыть", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: order_history_dialog.dismiss()
                ),
            ),
            size_hint=(0.85, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )

        order_history_dialog.open()

    def order_delete(self, order: Order):
        self.order_menu.dismiss()

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Удалить заказ?",
                theme_text_color="Custom",
                text_color="black"),
            MDDialogSupportingText(
                text=f"Удалить заказ №{order.order_id}?",
                theme_text_color="Custom",
                text_color="black"),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(
                        text="Отмена",
                        theme_text_color="Custom",
                        text_color="black"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(
                        text="Удалить",
                        theme_text_color="Custom",
                        text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: self.confirm_delete(order, dialog)
                ),
            ),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def confirm_delete(self, order: Order, dialog):
        app = MDApp.get_running_app()
        app.shift.delete_order(order)

        dialog.dismiss()
        self.order_list_update()
        self.order_list_total_value_update()

    def order_qr_code(self, order: Order):
        self.order_menu.dismiss()
        if order.cafe_user_id:
            self.snack_bar("QR-код уже использован!")
        else:
            self.show_order_confirmation(order)

    def show_order_menu(self, button, order):
        order_menu = [
            {
                "text": "QR",
                "leading_icon": "qrcode",
                "on_release": lambda x=None, o=order: self.order_qr_code(o),
            },
            {
                "text": "Удалить",
                "leading_icon": "trash-can-outline",
                "on_release": lambda x=None, o=order: self.order_delete(o),
            },
        ]

        self.order_menu = MDDropdownMenu(items=order_menu, )
        self.order_menu.caller = button
        self.order_menu.open()

    def show_order_details(self, order):
        # Создаем основной контейнер
        main_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(10),
            adaptive_height=True
        )

        # Шапка с номером заказа и временем
        header_box = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=5,
            padding=[5, 5, 5, 5],
        )

        order_id_label = MDLabel(
            text=f"Заказ №{order.order_id}",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=dp(25)
        )

        time_label = MDLabel(
            text=f"{order.created_at}",
            halign="right",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=dp(25)
        )

        header_box.add_widget(order_id_label)
        header_box.add_widget(time_label)

        # Контейнер для товаров
        items_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            adaptive_height=True
        )

        # Список товаров
        for idx, item in enumerate(order.items):
            item_box = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True,
                spacing=dp(10)
            )

            # Название товара
            name_label = MDLabel(
                text=f"{idx + 1} {item.drink.name} {item.drink.size} {item.drink.size_unit} x {item.quantity}",
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.5,
                size_hint_y=None,
                height=dp(30)
            )

            total_label = MDLabel(
                text=f"{item.total_price} BYN",
                theme_text_color="Custom",
                text_color="black",
                halign="right",
                size_hint_x=0.2,
                size_hint_y=None,
                height=dp(30)
            )

            item_box.add_widget(name_label)
            item_box.add_widget(total_label)

            items_container.add_widget(item_box)

        footer_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
        )

        total_title = MDLabel(
            text="Итого:",
            theme_text_color="Custom",
            text_color="black",
            font_size="18sp",
            size_hint_x=0.5,
        )

        total_amount = MDLabel(
            text=f"{order.drink_amount}"
                 f" {'позиций' if order.drink_amount > 4 else 'позиции' if order.drink_amount > 1 else 'позиция'}",
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            font_size="22sp",
            size_hint_x=0.3,
            halign="right"
        )

        total_value = MDLabel(
            text=f"{order.total_price} {'PIG' if order.is_free else 'BYN'}",
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            font_size="22sp",
            size_hint_x=0.3,
            halign="right"
        )

        footer_box.add_widget(total_title)
        footer_box.add_widget(total_amount)
        footer_box.add_widget(total_value)

        # Собираем все вместе
        # main_container.add_widget(header_box)
        # main_container.add_widget(MDDivider())
        main_container.add_widget(items_container)
        # main_container.add_widget(MDDivider())
        # main_container.add_widget(footer_box)

        scroll_view = MDScrollView(
            size_hint=(1, None),
            height=dp(200)
        )
        scroll_view.add_widget(main_container)

        order_details_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Детали заказа",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogContentContainer(
                header_box,
                MDDivider(),
                scroll_view,
                MDDivider(),
                footer_box,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Закрыть", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: order_details_dialog.dismiss()
                ),
            ),
            size_hint=(0.8, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )

        order_details_dialog.open()

    def show_shifts(self):
        self.toolbar_menu.dismiss()

        app = MDApp.get_running_app()
        shifts = app.shift.get_all_shifts(app.shift.barista)

        if not shifts:
            self.snack_bar("История смен пуста")
            return

        header_box = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=5,
            padding=[5, 5, 5, 5],
        )

        shift_date_label = MDLabel(
            text="Смены",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=dp(25)
        )

        barista_label = MDLabel(
            text=f"Бариста {app.shift.barista.name}",
            halign="right",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=dp(25)
        )

        header_box.add_widget(shift_date_label)
        header_box.add_widget(barista_label)

        self.shift_list = MDList()
        self.shift_list_update(shifts)

        shift_list_scroll_view = MDScrollView(
            size_hint_y=None,
            height=dp(300)
        )
        shift_list_scroll_view.add_widget(self.shift_list)

        self.shift_total_value = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            spacing=5,
            padding=[5, 5, 5, 5],
        )
        self.shift_list_total_value_update(shifts)

        shifts_history_dialog = MDDialog(
            MDDialogHeadlineText(text="История смен", theme_text_color="Custom", text_color="black"),
            MDDialogContentContainer(
                header_box,
                MDDivider(),
                shift_list_scroll_view,
                MDDivider(),
                self.shift_total_value,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Закрыть", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: shifts_history_dialog.dismiss()
                ),
            ),
            size_hint=(0.9, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        shifts_history_dialog.open()

    def shift_list_update(self, shifts_list=None):
        self.shift_list.clear_widgets()

        app = MDApp.get_running_app()
        shifts = shifts_list or app.shift.get_all_shifts(app.shift.barista)

        for shift in reversed(shifts):
            time_text = f"{shift.start_time.strftime('%H:%M')} - {shift.end_time.strftime('%H:%M') if shift.end_time else 'Не закрыта'}"

            shift_list_item = MDListItem(
                MDListItemHeadlineText(
                    text=f"Смена {shift.start_time.strftime('%d.%m.%Y')}",
                    theme_text_color="Custom",
                    text_color="black",
                    font_style="Title",
                    role="medium",
                    bold=False
                ),
                MDListItemSupportingText(
                    text=time_text,
                    theme_text_color="Custom",
                    text_color="black",
                    font_style="Title",
                    role="small",
                    bold=False
                ),
                MDListItemTertiaryText(
                    text=f"{shift.order_amount} "
                         f"{'заказов' if shift.order_amount > 4 else 'заказа' if shift.order_amount > 1 else 'заказ'} "
                         f"на сумму {shift.revenue} BYN",
                    theme_text_color="Custom",
                    text_color="black",
                    font_style="Title",
                    role="small",
                    bold=False
                ),
                MDIconButton(
                    icon="dots-vertical",
                    theme_icon_color="Custom",
                    icon_color="black",
                    theme_bg_color="Custom",
                    md_bg_color="white",
                    pos_hint={"center_x": 0.5, "center_y": 0.7},
                    on_release=lambda x, s=shift: self.show_shift_menu(x, s)
                ),
                divider=True,
                divider_color="black",
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                on_release=lambda x, s=shift: self.show_shift_order_history(s)
            )
            self.shift_list.add_widget(shift_list_item)

    def shift_list_total_value_update(self, shifts_list=None):
        self.shift_total_value.clear_widgets()

        app = MDApp.get_running_app()
        shifts = shifts_list or app.shift.get_all_shifts(app.shift.barista)

        total_label = MDLabel(
            text="Всего:",
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(20),
            size_hint_x=0.3
        )

        total_amount = len(shifts)
        total_hours = sum(shift.total_hours for shift in shifts if shift.total_hours)

        shifts_text = f"{total_amount} {'смен' if total_amount > 4 else 'смены' if total_amount > 1 else 'смена'}"
        cart_total_amount_label = MDLabel(
            text=shifts_text,
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(20),
            bold=True,
            halign="right",
            size_hint_x=0.5
        )

        cart_total_value_label = MDLabel(
            text=f"{total_hours} часов",
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(20),
            bold=True,
            halign="right",
            size_hint_x=0.5
        )

        self.shift_total_value.add_widget(total_label)
        self.shift_total_value.add_widget(cart_total_amount_label)
        self.shift_total_value.add_widget(cart_total_value_label)

    def show_shift_menu(self, button, shift):
        pass

    def switch_barista(self):
        """Смена бариста"""
        self.toolbar_menu.dismiss()
        self.manager.current = "barista_menu"

    def show_close_shift_dialog(self, *args):
        """Показать диалог закрытия смены"""
        app = MDApp.get_running_app()

        total_orders = len(app.shift.orders)

        total_revenue = 0
        total_points = 0
        for order in app.shift.orders:
            if order.is_free:
                total_points += order.total_price
            else:
                total_revenue += order.total_price

        dialog = MDDialog(
            MDDialogHeadlineText(text="Закрыть смену?", theme_text_color="Custom", text_color="black"),
            MDDialogSupportingText(text="Желаете закрыть смену?\n\n"
                                        f"Заказов за смену: {total_orders}\n"
                                        f"Выручка: {total_revenue} BYN\n"
                                        f"Убытки: {total_points} PIG",
                                   theme_text_color="Custom", text_color="black"),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Свернуть", theme_text_color="Custom", text_color="black"),
                    style="text",
                    # theme_bg_color="Custom",
                    # md_bg_color="pink",
                    on_release=lambda x: self.collapse_shift(dialog)
                ),
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
                    on_release=lambda x: self.close_shift(dialog)
                ),
            ),

            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )

        dialog.open()

    def collapse_shift(self, dialog):
        dialog.dismiss()

        self.manager.current = "login_menu"

        self.snack_bar("Смена свернута")

    def close_shift(self, dialog):
        dialog.dismiss()

        app = MDApp.get_running_app()

        app.barista = None
        app.shift.close()
        app.cart.clear()

        self.update_cart_counter()
        self.reset_card_counter()

        self.manager.current = "login_menu"

        self.snack_bar("Смена успешно закрыта")
