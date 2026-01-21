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
from kivymd.uix.dropdownitem import MDDropDownItem, MDDropDownItemText
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItemHeadlineText, MDListItem, MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.widget import MDWidget

from headers import Order, Barista, SECONDARY_COLOR, TOP_APP_BAR_COLOR, FOURTH_COLOR, CATEGORIES, PRODUCTS, Category


class CafeMenuScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main_menu"
        self.md_bg_color = "white"

        self.top_app_bar = None
        self.toolbar_menu = None

        self.categories_panel = None
        self.categories_list = None

        self.products_panel = None
        self.products_label = None
        self.product_card_quantity_labels = {}
        self.products_list = None
        self.cart_button = None
        self.cart_list = None

        self.selected_category = CATEGORIES[0]
        self.barista = None

        self.scroll_view = None
        self.cart_total_value_label = None

        self.build_ui()

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
                "on_release": self.show_shifts_history,
            },
        ]

        self.toolbar_menu = MDDropdownMenu(items=menu_items)

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
                text=f"Бариста {self.barista.name if self.barista else "Бариста"}",
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
        self.categories_list.clear_widgets()

        for category in CATEGORIES:
            item = MDListItem(
                # MDListItemLeadingIcon(icon=category["icon"]),
                MDListItemHeadlineText(
                    text=category.name,
                    theme_text_color="Custom",
                    text_color="black",
                ),
                theme_bg_color="Custom",
                md_bg_color="pink" if category == self.selected_category else FOURTH_COLOR,
                on_release=lambda x, cat=category: self.select_category(cat),
                size_hint_y=None,
                height="60dp"
            )

            self.categories_list.add_widget(item)

    def categories_panel_init(self):
        self.categories_panel = MDBoxLayout(
            orientation="vertical",
            size_hint=(0.25, 1),
            padding=5,
            spacing=5,
            radius=[5, 5, 5, 5],
            theme_bg_color="Custom",
            md_bg_color=FOURTH_COLOR
        )

        categories_label = MDLabel(
            text="Категории",
            halign="center",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height="50dp",
            font_size="20sp",
            bold=True
        )

        self.categories_list = MDList()

        scroll_view_categories_list = MDScrollView()
        scroll_view_categories_list.add_widget(self.categories_list)

        self.categories_panel.add_widget(categories_label)
        self.categories_panel.add_widget(scroll_view_categories_list)

        self.categories_panel_list_update()

    def products_panel_list_update(self):
        app = MDApp.get_running_app()

        self.products_list.clear_widgets()
        self.products_list.parent.scroll_y = 1.0

        products = sorted([p for p in PRODUCTS if p.category_id == self.selected_category.category_id], key=lambda x: x.name)

        for product in products:
            # Создаем карточку продукта
            card = MDCard(
                orientation="vertical",
                size_hint_y=None,
                height=dp(120),
                padding=[dp(10), dp(5), dp(10), dp(5)],
                spacing=dp(10),
                elevation=2,
                radius=[dp(10), dp(10), dp(10), dp(10)],
                theme_bg_color="Custom",
                md_bg_color=SECONDARY_COLOR,
                style="filled"
            )

            card_layout = MDRelativeLayout()
            card.add_widget(card_layout)

            # Верхняя строка: название и цена
            top_row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(30),
                pos_hint={"center_y": 0.6}
            )

            # Название продукта
            product_name_label = MDLabel(
                text=f"{product.name} {product.selected_size} {product.size_unit}",
                halign="left",
                padding=10,
                theme_text_color="Custom",
                text_color="black",
                bold=True,
                size_hint_x=0.7,
            )

            # Цена продукта - используем метод display_price
            price_label = MDLabel(
                text=f"{product.selected_price} BYN",
                halign="right",
                padding=10,
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.3,
                bold=True
            )

            top_row.add_widget(product_name_label)
            top_row.add_widget(price_label)
            card_layout.add_widget(top_row)

            # Нижняя строка: выбор размера (если есть) и кнопки
            bottom_row = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(40),
                spacing=dp(10)
            )

            # Контейнер для кнопок размеров
            size_container = MDBoxLayout(
                orientation="horizontal",
                spacing=5,
                padding=10,
                size_hint_x=0.6
            )

            len_sizes = len(product.sizes)
            if len_sizes > 1:
                for i in range(len_sizes):
                    size_button = MDButton(
                        MDButtonText(
                            text=f"{product.sizes_label[i]}",
                            theme_text_color="Custom",
                            text_color="black",
                            font_size=dp(10)
                        ),
                        size_hint=(None, None),
                        size=(dp(40), dp(35)),
                        theme_bg_color="Custom",
                        md_bg_color="pink" if i == 0 else "white",
                    )

                    size_button.bind(on_release=lambda x, p=product, n=i: self.select_size(x, p, n))

                    size_container.add_widget(size_button)

            bottom_row.add_widget(size_container)

            # Кнопки добавления/удаления
            buttons_container = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(5),
                padding=2,
                size_hint_x=0.3
            )

            # Кнопка уменьшения количества
            pop_button = MDIconButton(
                icon="minus",
                theme_text_color="Custom",
                text_color="black",
                theme_bg_color="Custom",
                md_bg_color=SECONDARY_COLOR,
                # size_hint=(None, None),
                # size=(dp(30), dp(30))
            )
            pop_button.bind(on_release=lambda x, p=product: self.pop_from_cart(p))

            product_amount = sum(item.quantity for item in app.cart.cart_items if item.product.product_id == product.product_id)

            # Поле для отображения количества в корзине
            quantity_label = MDLabel(
                text=str(product_amount),
                theme_text_color="Custom",
                text_color="black",
                halign="center",
                # valign="center",
                # size_hint_x=0.2,
                bold=True
            )

            self.product_card_quantity_labels[product.product_id] = quantity_label

            # Кнопка увеличения количества
            add_button = MDIconButton(
                icon="plus",
                theme_text_color="Custom",
                text_color="black",
                theme_bg_color="Custom",
                md_bg_color=SECONDARY_COLOR,
                # size_hint=(None, None),
                # size=(dp(30), dp(30))
            )
            add_button.bind(on_release=lambda x, p=product: self.add_to_cart(p))

            buttons_container.add_widget(pop_button)
            buttons_container.add_widget(quantity_label)
            buttons_container.add_widget(add_button)

            bottom_row.add_widget(buttons_container)
            card.add_widget(bottom_row)

            self.products_list.add_widget(card)

    def products_panel_init(self):
        self.products_panel = MDBoxLayout(
            orientation="vertical",
            size_hint=(0.75, 1.0),
            spacing=10,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            theme_bg_color="Primary",
            # md_bg_color=SECONDARY_COLOR
        )

        self.products_label = MDLabel(
            text="Кофе",
            halign="center",
            theme_text_color="Custom",
            text_color="black",
            adaptive_height=True,
            font_style="Headline",
            role="small",
            bold=True,
            radius=(5, 5, 5, 5),
            theme_bg_color="Custom",
            md_bg_color=FOURTH_COLOR
        )

        self.products_list = MDList(
            padding=15,
            spacing=15,
            size_hint=(0.95, 0.95),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )

        self.cart_button = MDButton(
            MDButtonIcon(
                icon="cart",
                pos_hint={"center_x": 0.44, "center_y": 0.5},
                theme_text_color="Custom",
                text_color="black"),
            MDButtonText(
                id="text",
                text="0 BYN",
                theme_text_color="Custom",
                text_color="black",
                pos_hint={"center_x": 0.56, "center_y": 0.5}
            ),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color="pink",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            height="50dp",
            theme_width="Custom",
            size_hint=(0.8, 0.8),
            on_release=self.show_cart
        )

        products_scroll = MDScrollView()
        products_scroll.add_widget(self.products_list)

        self.products_panel.add_widget(self.products_label)
        self.products_panel.add_widget(products_scroll)
        self.products_panel.add_widget(self.cart_button)

        self.products_panel_list_update()

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
        self.products_panel_init()

        content_layout.add_widget(self.categories_panel)
        content_layout.add_widget(self.products_panel)

        main_layout.add_widget(self.top_app_bar)
        main_layout.add_widget(content_layout)

        self.add_widget(main_layout)

    def select_category(self, category: Category):
        self.selected_category = category

        self.products_label.text = self.selected_category.name

        self.categories_panel_list_update()
        self.products_panel_list_update()

    def select_size(self, button, product, size_num):
        for btn in button.parent.children:
            btn.md_bg_color = "white"

        button.md_bg_color = "pink"

        # Сохраняем выбранный размер для продукта
        product.selected_size = product.sizes[size_num]
        product.selected_price = product.prices[size_num]

        button.parent.parent.parent.children[1].children[0].children[1].text = f"{product.name} {product.selected_size} {product.size_unit}"
        button.parent.parent.parent.children[1].children[0].children[0].text = f"{product.selected_price} BYN"

    # Метод добавления в корзину
    def add_to_cart(self, product, size=None):
        app = MDApp.get_running_app()

        app.cart.add(product, size or product.selected_size)

        self.update_cart_counter()
        self.update_card_counter(product.product_id)
        self.cart_items_update()

    # Метод удаления из корзины
    def pop_from_cart(self, product, size=None):
        app = MDApp.get_running_app()

        app.cart.pop(product, size or product.selected_size)

        self.update_cart_counter()
        self.update_card_counter(product.product_id)
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

    def update_card_counter(self, product_id):
        app = MDApp.get_running_app()

        product_amount = sum(item.quantity for item in app.cart.cart_items if item.product.product_id == product_id)
        card_quantity_label = self.product_card_quantity_labels.get(product_id)
        if card_quantity_label and isinstance(card_quantity_label, MDLabel):
            card_quantity_label.text = str(product_amount)

    def reset_card_counter(self):
        for card in self.products_list.children:
            if isinstance(card, MDCard):
                label = card.children[0].children[0].children[1]
                if isinstance(label, MDLabel):
                    label.text = "0"

    def update_cart_counter(self):
        app = MDApp.get_running_app()

        if hasattr(self, 'cart_button'):
            for child in self.cart_button.children:
                if isinstance(child, MDButtonText):
                    child.text = f"{(sum(item.total for item in app.cart.cart_items))} BYN"
                    break

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

        total_amount = 0

        for i, cart_item in enumerate(sorted(app.cart.cart_items, key=lambda x: x.product.name)):
            item_layout = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(50),
                spacing=5,
                padding=5,
            )

            item_info = MDLabel(
                valign="bottom",
                text=f"{cart_item.name} {cart_item.size} {cart_item.size_unit} x {cart_item.quantity}",
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.5
            )

            item_total = MDLabel(
                valign="bottom",
                halign="center",
                text=f"{cart_item.total} BYN",
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

            # Кнопка уменьшения количества
            pop_button = MDIconButton(
                icon="minus",
                theme_text_color="Custom",
                text_color="black",
                theme_bg_color="Custom",
                md_bg_color=SECONDARY_COLOR,
                # size_hint=(None, None),
                # size=(dp(30), dp(30))
            )
            pop_button.bind(on_release=lambda x, p=cart_item.product, s=cart_item.size: self.pop_from_cart(p, s))

            item_amount = sum(item.quantity for item in app.cart.cart_items if item.product.product_id == cart_item.product.product_id
                              and item.size == cart_item.size)

            # Поле для отображения количества в корзине
            quantity_label = MDLabel(
                text=str(item_amount),
                theme_text_color="Custom",
                text_color="black",
                halign="center",
                valign="bottom",
                # valign="center",
                # size_hint_x=0.2,
                bold=True
            )

            # Кнопка увеличения количества
            add_button = MDIconButton(
                icon="plus",
                theme_text_color="Custom",
                text_color="black",
                theme_bg_color="Custom",
                md_bg_color=SECONDARY_COLOR,
                # size_hint=(None, None),
                # size=(dp(30), dp(30))
            )
            add_button.bind(on_release=lambda x, p=cart_item.product, s=cart_item.size: self.add_to_cart(p, s))

            buttons_container.add_widget(pop_button)
            buttons_container.add_widget(quantity_label)
            buttons_container.add_widget(add_button)

            item_layout.add_widget(item_info)
            item_layout.add_widget(item_total)
            item_layout.add_widget(buttons_container)

            cart_content.add_widget(item_layout)

            total_amount += cart_item.total

        self.cart_total_value_label.text = f"{total_amount} BYN"

        self.scroll_view.add_widget(cart_content)

    def show_cart(self, *args):
        app = MDApp.get_running_app()

        if not hasattr(app, 'cart') or not app.cart.cart_items:
            MDSnackbar(
                MDSnackbarText(text="Корзина пуста", theme_text_color="Custom", text_color="black"),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.5,
                theme_bg_color="Primary",
                radius=[10, 10, 10, 10],
                duration=1,
            ).open()
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
            height=dp(300)
        )

        self.cart_items_update()

        dialog = MDDialog(
            MDDialogHeadlineText(text="Корзина", theme_text_color="Custom", text_color="black"),
            MDDialogContentContainer(
                MDDivider(),
                self.scroll_view,
                MDDivider(),
                total_layout,
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
                    MDButtonText(text="Оформить заказ", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: self.create_order(dialog)
                ),
            ),
            theme_bg_color="Custom",
            md_bg_color="white"
        )
        dialog.open()

    def create_order(self, dialog):
        app = MDApp.get_running_app()

        if not hasattr(app, 'cart') or not app.cart.cart_items:
            dialog.dismiss()
            return

        order_id = len(app.shift.orders) + 1

        order = Order(order_id, app.barista)
        for cart_item in app.cart.cart_items:
            order.add_item(cart_item)

        app.shift.add_order(order)
        app.cart.clear()

        dialog.dismiss()

        self.update_cart_counter()
        self.reset_card_counter()

        self.show_order_confirmation(order)

    def show_order_confirmation(self, order):
        items_text = "\n".join([f"{num + 1}. {item.name} x {item.quantity} - {item.total} BYN"
                                for num, item in enumerate(order.items)])

        dialog = MDDialog(
            MDDialogHeadlineText(text="Заказ успешно оформлен!", theme_text_color="Custom", text_color="black"),
            MDDialogSupportingText(text=f"Номер заказа: №{order.order_id}\n"
                                        f"Время: {order.created_at}\n\n"
                                        f"{items_text}\n\n"
                                        f"Итого: {order.total_amount} BYN",
                                   theme_text_color="Custom", text_color="black"),
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
            md_bg_color="white"
        )
        dialog.open()

    def show_order_history(self):
        self.toolbar_menu.dismiss()

        app = MDApp.get_running_app()

        if not app.shift.orders:
            MDSnackbar(
                MDSnackbarText(text="История заказов пуста", theme_text_color="Custom", text_color="black"),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.5,
                theme_bg_color="Primary",
                radius=[10, 10, 10, 10],
                duration=1,
            ).open()

            return

        history_content = MDBoxLayout(
            orientation="vertical",
            padding=10,
            size_hint_y=None
        )
        history_content.bind(minimum_height=history_content.setter('height'))

        total = 0

        for order in reversed(app.shift.orders[-10:]):
            order_card = MDBoxLayout(
                orientation="vertical",
                spacing=dp(10),
                padding=10,
                adaptive_height=True
            )

            order_header = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True
            )

            order_id_label = MDLabel(
                text=f"Заказ №{order.order_id}",
                theme_text_color="Custom",
                text_color="black",
                bold=True,
                size_hint_x=0.6
            )

            order_time = MDLabel(
                text=order.created_at,
                theme_text_color="Custom",
                text_color="black",
                halign="right",
                font_size="12sp",
                size_hint_x=0.4
            )

            total += order.total_amount

            order_details_header = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True
            )

            order_details = MDLabel(
                text=f"{len(order.items)} товаров на сумму {order.total_amount} BYN",
                theme_text_color="Custom",
                text_color="black",
                size_hint_y=None,
                height="30dp"
            )

            details_button = MDIconButton(
                icon="more",
                style="standard",
                theme_bg_color="Custom",
                md_bg_color="white",
                theme_icon_color="Custom",
                icon_color=SECONDARY_COLOR
            )
            details_button.bind(on_release=lambda x: self.show_order_details(order))

            order_header.add_widget(order_id_label)
            order_header.add_widget(order_time)

            order_details_header.add_widget(order_details)
            order_details_header.add_widget(details_button)

            order_card.add_widget(order_header)
            order_card.add_widget(order_details_header)

            history_content.add_widget(order_card)

        scroll_view = MDScrollView(
            size_hint=(1, None),
            height=dp(300)
        )

        scroll_view.add_widget(history_content)

        total_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            spacing=5,
            padding=[5, 5, 15, 5],
        )

        total_label = MDLabel(
            text="Всего:",
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(20),
            bold=True,
            size_hint_x=0.5
        )

        cart_total_value_label = MDLabel(
            text=f"{total} BYN",
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(20),
            bold=True,
            halign="right",
            size_hint_x=0.5
        )

        total_layout.add_widget(total_label)
        total_layout.add_widget(cart_total_value_label)

        dialog = MDDialog(
            MDDialogHeadlineText(text="История заказов", theme_text_color="Custom", text_color="black"),
            MDDialogContentContainer(
                MDDivider(),
                scroll_view,
                MDDivider(),
                total_layout,
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
            theme_bg_color="Custom",
            md_bg_color="white"
        )
        dialog.open()

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
            spacing=dp(5),
            adaptive_height=True
        )

        order_id_label = MDLabel(
            text=f"Заказ №{order.order_id}",
            theme_text_color="Custom",
            text_color="black",
            bold=True,
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
                text=f"{idx + 1} {item.name} x {item.quantity}",
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.5,
                size_hint_y=None,
                height=dp(30)
            )

            total_label = MDLabel(
                text=f"{item.total} BYN",
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
            halign="right"
        )

        total_title = MDLabel(
            text="Итого:",
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            font_size="18sp",
            size_hint_x=0.5,
            halign="right"
        )

        total_value = MDLabel(
            text=f"{order.total_amount} BYN",
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            font_size="22sp",
            size_hint_x=0.3
        )

        footer_box.add_widget(total_title)
        footer_box.add_widget(total_value)

        # Собираем все вместе
        main_container.add_widget(header_box)
        main_container.add_widget(MDDivider())
        main_container.add_widget(items_container)
        main_container.add_widget(MDDivider())
        main_container.add_widget(footer_box)

        # Создаем диалог
        self.order_details_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Детали заказа",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogContentContainer(
                MDScrollView(
                    main_container,
                    size_hint=(1, None),
                    height=dp(min(400, 150 + len(order.items) * 40))
                ),
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="ОК"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color=SECONDARY_COLOR,
                    on_release=lambda x: self.order_details_dialog.dismiss()
                ),
            ),
            size_hint=(0.85, None),
            height=dp(min(500, 200 + len(order.items) * 45)),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[20, 20, 20, 20]
        )

        self.order_details_dialog.open()

    def show_shifts_history(self):
        """Показать историю смен"""
        self.toolbar_menu.dismiss()

        app = MDApp.get_running_app()

        if not hasattr(app, 'shifts_history') or not app.shifts_history:
            MDSnackbar(
                MDSnackbarText(text="История смен пуста", theme_text_color="Custom", text_color="black"),
                y=dp(24),
                pos_hint={"center_x": 0.5},
                size_hint_x=0.5,
                theme_bg_color="Primary",
                radius=[10, 10, 10, 10],
                duration=1,
            ).open()
            return

        history_content = MDBoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        history_content.bind(minimum_height=history_content.setter('height'))

        for shift in reversed(app.shifts_history[-5:]):  # Последние 5 смен
            shift_data = shift.to_dict()

            shift_card = MDCard(
                orientation="vertical",
                padding=10,
                size_hint_y=None,
                height="120dp",
                elevation=1,
                md_bg_color=(0.98, 0.98, 0.98, 1)
            )

            # Заголовок смены
            shift_header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="30dp")
            barista_label = MDLabel(
                text=f"👤 {shift_data['barista']}",
                theme_text_color="Custom",
                text_color="black",
                bold=True,
                size_hint_x=0.6
            )
            status_label = MDLabel(
                text=f"🟢 Активна" if shift_data['status'] == "active" else f"🔴 Завершена",
                theme_text_color="Custom",
                text_color="green" if shift_data['status'] == "active" else "red",
                halign="right",
                size_hint_x=0.4
            )

            shift_header.add_widget(barista_label)
            shift_header.add_widget(status_label)
            shift_card.add_widget(shift_header)

            # Время смены
            time_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="25dp")
            start_time = MDLabel(
                text=f"🕒 Начало: {shift_data['start_time']}",
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.5
            )
            end_time = MDLabel(
                text=f"⏰ Конец: {shift_data['end_time']}" if shift_data['end_time'] else "⏳ В процессе",
                theme_text_color="Custom",
                text_color="black",
                halign="right",
                size_hint_x=0.5
            )

            time_layout.add_widget(start_time)
            time_layout.add_widget(end_time)
            shift_card.add_widget(time_layout)

            # Статистика смены
            stats_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="25dp")
            orders_label = MDLabel(
                text=f"📦 Заказов: {shift_data['orders_count']}",
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.5
            )
            revenue_label = MDLabel(
                text=f"💰 Выручка: {shift_data['revenue']} BYN",
                theme_text_color="Custom",
                text_color="black",
                halign="right",
                size_hint_x=0.5
            )

            stats_layout.add_widget(orders_label)
            stats_layout.add_widget(revenue_label)
            shift_card.add_widget(stats_layout)

            # Длительность смены (если есть)
            if shift_data['duration']:
                duration_label = MDLabel(
                    text=f"⏱ Длительность: {shift_data['duration']}",
                    theme_text_color="Custom",
                    text_color="black",
                    size_hint_y=None,
                    height="25dp"
                )
                shift_card.add_widget(duration_label)

            history_content.add_widget(shift_card)

        scroll_view = MDScrollView(size_hint=(1, 0.7))
        scroll_view.add_widget(history_content)

        dialog = MDDialog(
            MDDialogHeadlineText(text="Смены", theme_text_color="Custom", text_color="black"),
            scroll_view,
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Закрыть", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: dialog.dismiss()
                ),
            ),
            size_hint=(0.9, 0.8)
        )
        dialog.open()

    def switch_barista(self):
        """Смена бариста"""
        self.toolbar_menu.dismiss()
        self.manager.current = "barista_menu"

    def show_close_shift_dialog(self, *args):
        """Показать диалог закрытия смены"""
        app = MDApp.get_running_app()

        total_orders = len(app.shift.orders)
        total_revenue = sum(order.total_amount for order in app.shift.orders)

        dialog = MDDialog(
            MDDialogHeadlineText(text="Закрыть смену", theme_text_color="Custom", text_color="black"),
            MDDialogSupportingText(text=f"Бариста: {app.barista.name}\n\n"
                                        f"Заказов за смену: {total_orders}\n"
                                        f"Выручка: {total_revenue} BYN\n\n"
                                        f"Желаете закрыть смену?",
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
                    on_release=lambda x: self.close_shift(dialog)
                ),
            ),

            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )

        dialog.open()

    def close_shift(self, dialog):
        dialog.dismiss()

        app = MDApp.get_running_app()

        app.barista = None
        app.shift.close()
        app.cart.clear()

        self.update_cart_counter()
        self.reset_card_counter()

        self.manager.current = "login_menu"

        MDSnackbar(
            MDSnackbarText(text="Смена успешно закрыта", theme_text_color="Custom", text_color="black"),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
            theme_bg_color="Primary",
            radius=[10, 10, 10, 10],
            duration=1,
        ).open()
