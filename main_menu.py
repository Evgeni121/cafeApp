from kivy.metrics import dp
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
from kivymd.uix.list import MDListItemHeadlineText, MDListItem, MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.segmentedbutton import MDSegmentedButton, MDSegmentedButtonItem, MDSegmentButtonLabel
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.widget import MDWidget

from common import snack_bar
from headers import Order, Barista, TOP_APP_BAR_COLOR, Category, Drink, MenuDrink
from order_menu import OrderMenu
from shift_menu import ShiftMenu


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

        self.shift_menu = None
        self.shift_list = None
        self.shift_total_value = None
        
        self.shift_menu = ShiftMenu()
        self.order_menu = OrderMenu()

        self.build_ui()

    def update_for_barista(self, barista: Barista):
        self.barista = barista

        if hasattr(self, 'top_app_bar'):
            child = self.top_app_bar.children[1].children[1].children[0]
            if isinstance(child, MDTopAppBarTitle):
                child.text = f"Бариста {self.barista.name}"

    def toolbar_menu_open(self, button):
        def show_orders():
            self.toolbar_menu.dismiss()
            self.order_menu.show_order_history()

        def show_shifts():
            self.toolbar_menu.dismiss()
            self.shift_menu.show_shifts()

        menu_items = [
            {
                "text": "Заказы",
                "leading_icon": "history",
                "on_release": show_orders,
            },
            {
                "text": "Смены",
                "leading_icon": "clock-time-three",
                "on_release": show_shifts,
            },
        ]

        self.toolbar_menu = MDDropdownMenu(
            items=menu_items,
            width=200,
            position="auto",
            caller=button,
        )

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
                size_hint_x=0.65,
            )

            price_label = MDLabel(
                text=f"{menu_drink.selected_drink.price:.2f} BYN",
                halign="right",
                padding=10,
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.35,
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
            0].text = f"{drink.price:.2f} BYN"

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
                size_hint_x=0.55
            )

            item_total = MDLabel(
                valign="bottom",
                halign="center",
                text=f"{cart_item.total_price:.2f} BYN",
                theme_text_color="Custom",
                text_color="black",
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                size_hint_x=0.2
            )

            # Кнопки добавления/удаления
            buttons_container = MDBoxLayout(
                orientation="horizontal",
                padding=[0, 0, 0, 5],
                size_hint_x=0.25
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
            snack_bar("Корзина пуста")
            return

        total_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=50,
            padding=5,
            spacing=5
        )

        total_label = MDLabel(
            text="Итого:",
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            size_hint_x=0.35
        )

        self.cart_total_value_label = MDLabel(
            text="0 BYN",
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            halign="right",
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

        if is_free and app.cart.discount > 0:
            snack_bar("Скидка на оплату баллами не распространяется!")
            return

        if not app.cart.cart_items:
            dialog.dismiss()
            return

        order = Order()
        order.discount = app.cart.discount
        for cart_item in app.cart.cart_items:
            order.add_item(cart_item)

        if is_free:
            self.order_menu.show_free_confirmation(order)
        else:
            app.shift.add_order(order)
            self.order_menu.show_order_confirmation(order)

        app.cart.clear()
        dialog.dismiss()

        self.update_cart_counter()
        self.reset_card_counter()

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
                total_revenue += order.discount_price

        dialog = MDDialog(
            MDDialogHeadlineText(text="Закрыть смену?", theme_text_color="Custom", text_color="black"),
            MDDialogSupportingText(text="Желаете закрыть смену?\n\n"
                                        f"Открыта: {app.shift.start_time.strftime('%H:%M')}\n"
                                        f"Заказов за смену: {total_orders}\n"
                                        f"Выручка: {total_revenue:.2f} BYN\n"
                                        f"Убытки: {total_points:.2f} PIG",
                                   theme_text_color="Custom", text_color="black"),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Свернуть", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: self.collapse_shift(dialog)
                ),
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

        snack_bar("Смена свернута")

    def close_shift(self, dialog):
        dialog.dismiss()

        app = MDApp.get_running_app()

        app.barista = None
        app.shift.close()
        app.cart.clear()

        self.update_cart_counter()
        self.reset_card_counter()

        self.manager.current = "login_menu"

        snack_bar("Смена успешно закрыта")
