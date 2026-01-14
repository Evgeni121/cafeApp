from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.appbar import MDTopAppBarTrailingButtonContainer, MDActionTopAppBarButton, MDTopAppBarTitle, \
    MDTopAppBarLeadingButtonContainer, MDTopAppBar
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton, MDButtonIcon
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialogButtonContainer, MDDialogHeadlineText, MDDialog, MDDialogSupportingText
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDListItemHeadlineText, MDListItem, MDList
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
from kivymd.uix.widget import MDWidget

from headers import Order, CartItem

PRIMARY_COLOR = "pink"
SECONDARY_COLOR = "lavenderblush"


class Product:
    def __init__(self, product_id, name, sizes, prices, category_id, calories):
        self._product_id = product_id
        self._name = name
        self._sizes = sizes
        self._prices = prices
        self._category_id = category_id
        self._calories = calories

    @property
    def product_id(self):
        return self._product_id

    @property
    def name(self):
        return self._name

    @property
    def sizes(self):
        return self._sizes

    @property
    def prices(self):
        return self._prices

    @property
    def category_id(self):
        return self._category_id


PRODUCTS = [
    # Кофе (категория 1) - с размерами в мл
    Product(1, "Эспрессо", [30, 50], [100, 120], 1, 5),
    Product(2, "Капучино", [250, 350], [180, 200], 1, 150),
    Product(3, "Латте", [350], [280], 1, 180),
    Product(4, "Американо", [180, 250], [120, 140], 1, 10),
    Product(5, "Раф", [350], [240], 1, 250),

    # Чай (категория 2) - с размерами в мл
    Product(6, "Черный чай", [300, 400], [100, 120], 2, 2),
    Product(7, "Зеленый чай", [300, 400], [100, 120], 2, 1),
    Product(8, "Фруктовый чай", [300, 400], [150, 170], 2, 5),

    # Выпечка (категория 3) - с размерами в г
    Product(9, "Круассан", [100], [150], 3, 350),
    Product(10, "Булочка", [100], [80], 3, 280),
    Product(11, "Пирожок", [100], [120], 3, 320),

    # Десерты (категория 4) - с размерами в г
    Product(12, "Чизкейк", [100], [250], 4, 450),
    Product(13, "Тирамису", [100], [280], 4, 380),
    Product(14, "Макарун", [100], [90], 4, 120),

    # Напитки (категория 5) - с размерами в мл
    Product(15, "Кола", [250, 500], [100, 120], 5, 150),
    Product(16, "Сок", [200, 330], [130, 150], 5, 120),
    Product(17, "Вода", [330, 500], [70, 80], 5, 0),
]


class CafeMenuScreen(MDScreen):
    """Главное меню кафе с товарами и корзиной"""

    cart_total = NumericProperty(0)
    cart_count = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main_menu"
        self.md_bg_color = "white"

        self.selected_sizes = {}  # Хранит выбранные размеры по ID продукта: {product_id: {"size": "...", "price": ...}}
        self.quantity_labels = {}  # Хранит ссылки на метки количества: {product_id: MDLabel}
        self.size_buttons = {}

        self.categories = [
            {"id": 1, "name": "Кофе", "icon": "coffee"},
            {"id": 2, "name": "Кофе с молоком", "icon": "coffee"},
            {"id": 3, "name": "Не кофе", "icon": "cup-water"},
            {"id": 4, "name": "Холодные напитки", "icon": "cup-water"},
            {"id": 5, "name": "Горячие напитки", "icon": "cup-water"},
            {"id": 6, "name": "Чай", "icon": "tea"},
            {"id": 7, "name": "Авторские напитки", "icon": "cup-water"},
            {"id": 8, "name": "Десерты", "icon": "cake"},
            {"id": 9, "name": "Добавки", "icon": "cake"},
        ]

        self.selected_category_id = 1
        self.barista = None
        self.build_ui()

    def update_for_barista(self, barista):
        self.barista = barista
        if hasattr(self, 'top_app_bar'):
            child = self.top_app_bar.children[1].children[1].children[0]
            if isinstance(child, MDTopAppBarTitle):
                child.text = f"{self.barista.name}"

    def build_ui(self):
        # Основной layout
        main_layout = MDBoxLayout(orientation="vertical")

        # Верхняя панель с МЕНЮ СЛЕВА и кнопкой закрытия смены СПРАВА
        self.top_app_bar = MDTopAppBar(
            MDTopAppBarLeadingButtonContainer(
                MDActionTopAppBarButton(
                    icon="menu",
                    theme_text_color="Custom",
                    text_color="black",
                    on_release=self.open_toolbar_menu,
                )
            ),
            MDTopAppBarTitle(
                text=f"{self.barista.name if self.barista else "Бариста"}",
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
            md_bg_color=SECONDARY_COLOR
        )

        # Основной контент - корзина теперь ВНУТРИ контента
        content_layout = MDBoxLayout(
            orientation="horizontal",
            spacing=10,
            padding=10,
        )

        # Левая панель - категории
        categories_panel = MDBoxLayout(
            orientation="vertical",
            size_hint=(0.25, 1),
            padding=5,
            # elevation=2,
            spacing=5,
            radius=[5, 5, 5, 5],
            theme_bg_color="Custom",
            md_bg_color=SECONDARY_COLOR
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

        self.update_categories_list()

        categories_panel.add_widget(categories_label)
        categories_panel.add_widget(MDScrollView(self.categories_list))

        # Правая панель - товары
        products_panel = MDBoxLayout(
            orientation="vertical",
            size_hint=(0.75, 0.98),
            padding=10,
            spacing=20,
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
            bold=True
        )

        self.products_scroll = MDScrollView()
        self.products_list = MDList(
            padding=15,
            spacing=15,
            size_hint=(0.95, 0.95),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.update_products_list()

        # Отдельная кнопка корзины внизу СПРАВА поверх всего
        self.cart_button = MDButton(
            MDButtonIcon(icon="cart", theme_text_color="Custom", text_color="black"),
            MDButtonText(text="0", theme_text_color="Custom", text_color="black"),
            style="filled",
            theme_bg_color="Custom",
            md_bg_color="pink",
            pos_hint={"center_x": 0.9, "center_y": 0.5},
            on_release=self.show_cart
        )

        self.products_scroll.add_widget(self.products_list)
        products_panel.add_widget(self.products_label)
        products_panel.add_widget(self.products_scroll)
        products_panel.add_widget(self.cart_button)

        content_layout.add_widget(categories_panel)
        content_layout.add_widget(products_panel)

        main_layout.add_widget(self.top_app_bar)
        main_layout.add_widget(content_layout)

        # Используем RelativeLayout для кнопки корзины
        screen_layout = MDRelativeLayout()
        screen_layout.add_widget(main_layout)
        # screen_layout.add_widget(self.cart_button)

        self.add_widget(screen_layout)

        self.create_toolbar_menu()

    def create_toolbar_menu(self):
        """Меню с историей заказов, историей смен и сменой бариста"""
        menu_items = [
            {
                "text": "История заказов",
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

    def open_toolbar_menu(self, button):
        """Меню открывается СВЕРХУ от кнопки"""
        self.toolbar_menu.caller = button
        self.toolbar_menu.open()

    def update_categories_list(self):
        self.categories_list.clear_widgets()

        for category in self.categories:
            item = MDListItem(
                # MDListItemLeadingIcon(icon=category["icon"]),
                MDListItemHeadlineText(
                    text=category["name"],
                    theme_text_color="Custom",
                    text_color="black",
                ),
                theme_bg_color="Custom",
                md_bg_color="pink" if category["id"] == self.selected_category_id else SECONDARY_COLOR,
                on_release=lambda x, cat_id=category["id"]: self.select_category(cat_id),
                size_hint_y=None,
                height="60dp"
            )
            self.categories_list.add_widget(item)

    def select_category(self, category_id):
        self.selected_category_id = category_id
        category = next((c for c in self.categories if c["id"] == category_id), None)
        if category:
            self.products_label.text = category["name"]
            self.update_categories_list()
            self.update_products_list()

    def update_products_list(self):
        self.products_list.clear_widgets()

        filtered_products = [p for p in PRODUCTS if p.category_id == self.selected_category_id]

        for product in filtered_products:
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
            name_label = MDLabel(
                text=f"{product.name} ",
                halign="left",
                padding=10,
                theme_text_color="Custom",
                text_color="black",
                bold=True,
                size_hint_x=0.7,
            )

            # Цена продукта - используем метод display_price
            price_label = MDLabel(
                text=f"{product.prices[0]} BYN",
                halign="right",
                padding=10,
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.3,
                bold=True
            )

            top_row.add_widget(name_label)
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

            # Создаем кнопки для каждого размера
            for i, (size, price) in enumerate(zip(product.sizes, product.prices)):
                # Создаем кнопку размера
                size_button = MDButton(
                    MDButtonText(
                        text=f"{size} мл",
                        theme_text_color="Custom",
                        text_color="black",
                        font_size=dp(10)
                    ),
                    size_hint=(None, None),
                    size=(dp(40), dp(35)),
                    theme_bg_color="Custom",
                    md_bg_color="pink" if i == 0 else "white",
                )

                # Добавляем обработчик для выбора размера
                size_button.bind(on_release=lambda x, p=product, s=size, pr=price: self.select_size(p, s, pr, x))

                # Сохраняем ссылку на кнопку
                size_key = f"{product.product_id}_{size}"
                self.size_buttons[size_key] = size_button

                size_container.add_widget(size_button)

                # Устанавливаем размер как выбранный по умолчанию
                if i == 0:
                    self.selected_sizes[product.product_id] = {
                        "size": size,
                        "price": price
                    }

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

            # Поле для отображения количества в корзине
            quantity_label = MDLabel(
                text="0",
                theme_text_color="Custom",
                text_color="black",
                halign="center",
                # valign="center",
                # size_hint_x=0.2,
                bold=True
            )

            # Сохраняем ссылку для обновления количества
            self.quantity_labels[str(product.product_id)] = quantity_label

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

        # Обновляем счетчик корзины после загрузки продуктов
        self.update_cart_counter()

    def select_size(self, product, size, price, button):
        # Сбрасываем стиль всех кнопок размеров для этого продукта
        for key, btn in self.size_buttons.items():
            if key.startswith(f"{product.product_id}_"):
                btn.theme_bg_color = "Custom"
                btn.md_bg_color = "white"

                # Обновляем текст кнопки
                for child in btn.children:
                    if isinstance(child, MDButtonText):
                        child.text_color = "black"
                        break

        # Устанавливаем выбранный размер
        button.theme_bg_color = "Custom"
        button.md_bg_color = "pink"

        # Обновляем текст выбранной кнопки
        for child in button.children:
            if isinstance(child, MDButtonText):
                child.text_color = "black"
                break

        # Сохраняем выбранный размер для продукта
        self.selected_sizes[product.product_id] = {
            "size": size,
            "price": price
        }

    # Метод добавления в корзину
    def add_to_cart(self, product):
        app = MDApp.get_running_app()

        # Получаем выбранный размер (если есть)
        selected_size = self.selected_sizes.get(product.product_id)

        # Форматируем текст размера для отображения
        size_display = self.format_size_display(selected_size["size"])
        product_name = f"{product.name} ({size_display})"
        price = selected_size["price"]

        # Проверяем, есть ли уже такой продукт в корзине
        existing_item = None
        for item in app.cart_items:
            if item.name == product_name and item.price == price:
                existing_item = item
                break

        if existing_item:
            existing_item.quantity += 1
        else:
            cart_item = CartItem(product.product_id, product_name, price, 1)
            app.cart_items.append(cart_item)

        # Обновляем отображение количества
        if str(product.product_id) in self.quantity_labels:
            # Считаем общее количество всех вариантов этого продукта
            total_quantity = sum(item.quantity for item in app.cart_items
                                 if item.product_id == product.product_id)
            self.quantity_labels[str(product.product_id)].text = str(total_quantity)

        # Обновляем счетчик корзины
        self.update_cart_counter()

    # Метод удаления из корзины
    def pop_from_cart(self, product):
        app = MDApp.get_running_app()

        # Получаем выбранный размер (если есть)
        selected_size = self.selected_sizes.get(product.product_id)

        size_display = self.format_size_display(selected_size["size"])
        product_name = f"{product.name} ({size_display})"
        price = selected_size["price"]

        # Находим продукт в корзине
        item_to_remove = None
        for item in app.cart_items:
            if item.name == product_name and item.price == price:
                item_to_remove = item
                break

        if item_to_remove:
            if item_to_remove.quantity > 1:
                item_to_remove.quantity -= 1
            else:
                app.cart_items.remove(item_to_remove)

        # Обновляем отображение количества
        if str(product.product_id) in self.quantity_labels:
            total_quantity = sum(item.quantity for item in app.cart_items
                                 if item.product_id == product.product_id)
            self.quantity_labels[str(product.product_id)].text = str(total_quantity)

        # Обновляем счетчик корзины
        self.update_cart_counter()

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

    def update_cart_counter(self):
        app = MDApp.get_running_app()
        if hasattr(app, 'cart_items'):
            total_items = sum(item.quantity for item in app.cart_items)
            # Обновляем текст кнопки корзины
            if hasattr(self, 'cart_button'):
                # Находим MDButtonText внутри кнопки корзины
                for child in self.cart_button.children:
                    if isinstance(child, MDButtonText):
                        child.text = str(total_items)
                        break

    def show_cart(self, *args):
        app = MDApp.get_running_app()

        if not hasattr(app, 'cart_items') or not app.cart_items:
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

        cart_content = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        cart_content.bind(minimum_height=cart_content.setter('height'))

        total_amount = 0

        for i, cart_item in enumerate(app.cart_items):
            item_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))

            item_info = MDLabel(
                text=f"{cart_item.name} x{cart_item.quantity}",
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.5
            )

            item_total = MDLabel(
                text=f"{cart_item.total} BYN",
                theme_text_color="Custom",
                text_color="black",
                halign="right",
                size_hint_x=0.3
            )

            remove_btn = MDIconButton(
                icon="close",
                theme_text_color="Custom",
                text_color="black",
                theme_bg_color="Custom",
                md_bg_color="pink",
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                on_release=lambda x, idx=i: self.remove_from_cart(idx)
            )

            item_layout.add_widget(item_info)
            item_layout.add_widget(item_total)
            item_layout.add_widget(remove_btn)
            cart_content.add_widget(item_layout)

            total_amount += cart_item.total

        total_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(60))
        total_label = MDLabel(
            text="Итого:",
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(20),
            bold=True,
            size_hint_x=0.5
        )
        total_value = MDLabel(
            text=f"{total_amount} BYN",
            theme_text_color="Custom",
            text_color="black",
            font_size=dp(20),
            bold=True,
            halign="right",
            size_hint_x=0.5
        )
        total_layout.add_widget(total_label)
        total_layout.add_widget(total_value)
        cart_content.add_widget(total_layout)

        scroll_view = MDScrollView(size_hint=(1, 0.6))
        scroll_view.add_widget(cart_content)

        dialog = MDDialog(
            MDDialogHeadlineText(text="Корзина", theme_text_color="Custom", text_color="black"),
            scroll_view,
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Очистить", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: self.clear_cart(dialog)
                ),
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
                    on_release=lambda x: self.create_order(dialog, total_amount)
                ),
            ),
            size_hint=(0.9, 0.8)
        )
        dialog.open()

    def remove_from_cart(self, index):
        app = MDApp.get_running_app()

        if 0 <= index < len(app.cart_items):
            # Обновляем счетчик количества для продукта
            removed_item = app.cart_items[index]
            product_id = removed_item.product_id

            # Удаляем элемент
            del app.cart_items[index]

            # Обновляем отображение количества
            if str(product_id) in self.quantity_labels:
                total_quantity = sum(item.quantity for item in app.cart_items
                                     if item.product_id == product_id)
                self.quantity_labels[str(product_id)].text = str(total_quantity)

            # Обновляем счетчик корзины
            self.update_cart_counter()

            # Обновляем диалог корзины
            self.show_cart()

    def clear_cart(self, dialog):
        app = MDApp.get_running_app()
        app.cart_items.clear()
        dialog.dismiss()
        self.update_cart_counter()

        MDSnackbar(
            MDSnackbarText(text="Корзина очищена", theme_text_color="Custom", text_color="black"),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.5,
            theme_bg_color="Primary",
            radius=[10, 10, 10, 10],
            duration=1,
        ).open()

    def create_order(self, dialog, total_amount):
        app = MDApp.get_running_app()

        if not hasattr(app, 'cart_items') or not app.cart_items:
            dialog.dismiss()
            return

        order_id = app.order_counter
        app.order_counter += 1

        order = Order(order_id, app.current_barista)
        for cart_item in app.cart_items:
            order.add_item(cart_item)

        if not hasattr(app, 'orders'):
            app.orders = []
        app.orders.append(order)

        # Добавляем заказ в текущую смену
        if hasattr(app, 'current_shift'):
            app.current_shift.add_order(order)

        dialog.dismiss()
        app.cart_items.clear()
        self.update_cart_counter()

        self.show_order_confirmation(order)

    def show_order_confirmation(self, order):
        items_text = "\n".join([f"• {item.name} x{item.quantity} - {item.total} BYN"
                                for item in order.items])

        dialog = MDDialog(
            MDDialogHeadlineText(text="✅ Заказ оформлен!", theme_text_color="Custom", text_color="black"),
            MDDialogSupportingText(text=f"Номер заказа: #{order.order_id}\n"
                                        f"Время: {order.created_at}\n\n"
                                        f"{items_text}\n\n"
                                        f"💵 Итого: {order.total_amount} BYN",
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
        )
        dialog.open()

    def show_order_history(self):
        self.toolbar_menu.dismiss()

        app = MDApp.get_running_app()

        if not hasattr(app, 'orders') or not app.orders:
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

        history_content = MDBoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        history_content.bind(minimum_height=history_content.setter('height'))

        for order in reversed(app.orders[-10:]):
            order_card = MDCard(
                orientation="vertical",
                padding=10,
                size_hint_y=None,
                height="100dp",
                elevation=1,
                md_bg_color=(0.98, 0.98, 0.98, 1)
            )

            order_header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height="30dp")
            order_id_label = MDLabel(
                text=f"Заказ #{order.order_id}",
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

            order_details = MDLabel(
                text=f"{len(order.items)} товаров на сумму {order.total_amount} BYN",
                theme_text_color="Custom",
                text_color="black",
                size_hint_y=None,
                height="30dp"
            )

            order_header.add_widget(order_id_label)
            order_header.add_widget(order_time)
            order_card.add_widget(order_header)
            order_card.add_widget(order_details)
            history_content.add_widget(order_card)

        scroll_view = MDScrollView(size_hint=(1, 0.7))
        scroll_view.add_widget(history_content)

        dialog = MDDialog(
            MDDialogHeadlineText(text="📜 История заказов", theme_text_color="Custom", text_color="black"),
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

        if not hasattr(app, 'orders'):
            app.orders = []

        total_orders = len(app.orders)
        total_revenue = sum(order.total_amount for order in app.orders)

        dialog = MDDialog(
            MDDialogHeadlineText(text="Закрыть смену", theme_text_color="Custom", text_color="black"),
            MDDialogSupportingText(text=f"Бариста: {app.current_barista.name}\n\n"
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

        # Закрываем текущую смену
        if hasattr(app, 'current_shift'):
            app.current_shift.close_shift()

        app.shift_open = False
        app.current_barista = None
        if hasattr(app, 'cart_items'):
            app.cart_items.clear()
        if hasattr(app, 'orders'):
            app.orders.clear()
        app.order_counter = 1

        self.update_cart_counter()
        self.manager.current = "login_menu"

        bar = MDSnackbar(
            MDSnackbarText(text="Смена успешно закрыта", theme_text_color="Custom", text_color="black"),
            y=dp(24),
            pos_hint={"center_x": 0.5},
            size_hint_x=0.8,
            theme_bg_color="Primary",
            radius=[10, 10, 10, 10],
            duration=1,
        )

        bar.open()
