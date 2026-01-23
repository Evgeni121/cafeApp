from datetime import datetime

PRIMARY_COLOR = "pink"
SECONDARY_COLOR = "lavenderblush"
THIRD_COLOR = "snow"
FOURTH_COLOR = "snow"
TOP_APP_BAR_COLOR = "white"


class Category:
    def __init__(self, category_id, name):
        self._category_id = category_id
        self._name = name

    @property
    def category_id(self):
        return self._category_id

    @property
    def name(self):
        return self._name


CATEGORIES = [
    Category(1, "Кофе"),
    Category(2, "Кофе с молоком"),
    Category(3, "Не кофе"),
    Category(4, "Холодные напитки"),
    Category(5, "Горячие напитки"),
    Category(6, "Чай"),
    Category(7, "Авторские напитки"),
    Category(8, "Десерты"),
    Category(9, "Добавки"),
]


class Product:
    def __init__(self, product_id, name, sizes, prices, category_id, calories, sizes_label=None, volume=None):
        self._product_id = product_id
        self._name = name
        self._sizes = sizes
        self._prices = prices
        self._category_id = category_id
        self._calories = calories

        self._size_unit = "мл" if volume else "г"
        self._sizes_label = sizes_label

        self._selected_size = self._sizes[0]
        self._selected_price = self._prices[0]

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
    def sizes_label(self):
        return self._sizes_label

    @property
    def prices(self):
        return self._prices

    @property
    def size_unit(self):
        return self._size_unit

    @property
    def category_id(self):
        return self._category_id

    @property
    def selected_size(self):
        return self._selected_size

    @selected_size.setter
    def selected_size(self, selected_size):
        self._selected_size = selected_size

    @property
    def selected_price(self):
        return self._selected_price

    @selected_price.setter
    def selected_price(self, selected_price):
        self._selected_price = selected_price


PRODUCTS = [
    Product(1, "Эспрессо", [30, 50], [5, 6], 1, 5, ["S", "M"], True),
    Product(2, "Капучино", [250, 350], [6, 7.5], 1, 150, ["M", "L"], True),
    Product(3, "Латте", [350], [7], 1, 180, ["L"], True),
    Product(4, "Американо", [250, 350], [5, 6], 1, 10, ["M", "L"], True),
    Product(5, "Раф", [350], [9], 1, 250, ["L"], True),

    Product(6, "Черный чай", [350, 450], [5, 7], 6, 2, ["M", "L"], True),
    Product(7, "Зеленый чай", [350, 450], [5, 7], 6, 1, ["M", "L"], True),
    Product(8, "Фруктовый чай", [350, 450], [5.5, 7.5], 6, 5, ["M", "L"], True),

    Product(12, "Чизкейк", [100], [6], 8, 450),
    Product(13, "Тирамису", [100], [5], 8, 380),
    Product(14, "Макарун", [100], [4], 8, 120),

    Product(15, "Кола", [330], [2], 4, 150, False, True),
    Product(16, "Сок", [330], [2], 4, 120, False, True),
    Product(17, "Вода", [330], [1.5], 4, 0, False, True),
]


class Barista:
    def __init__(self, barista_id, name):
        self._barista_id = barista_id
        self._name = name

    @property
    def barista_id(self):
        return self._barista_id

    @barista_id.setter
    def barista_id(self, barista_id):
        self._barista_id = barista_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name


BARISTAS = [
    Barista(1, "Дашка"),
    Barista(2, "Кристина"),
    Barista(3, "Грета"),
]


class CartItem:
    """Элемент корзины"""

    def __init__(self, product, size, quantity=1):
        self.product = product
        self.name = product.name
        self.size = size
        self.size_unit = product.size_unit

        self.price = product.prices[product.sizes.index(size)]

        self.quantity = quantity

    @property
    def total(self):
        return self.price * self.quantity


class Cart:
    def __init__(self):
        self.cart_items: [CartItem] = []

    def add(self, product: Product, size):
        cart_item = next((cart_item for cart_item in self.cart_items if
                          cart_item.product.product_id == product.product_id and
                          cart_item.size == size), None)

        if cart_item:
            cart_item.quantity += 1
        else:
            self.cart_items.append(CartItem(product, size))

    def pop(self, product: Product, size):
        cart_item = next((cart_item for cart_item in self.cart_items if
                          cart_item.product.product_id == product.product_id and
                          size == cart_item.size), None)

        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                self.cart_items.remove(cart_item)

    @property
    def total(self):
        return sum(lambda x: item.total for item in self.cart_items)

    def clear(self):
        self.cart_items.clear()


class Order:
    """Заказ"""

    def __init__(self, order_id, barista_name):
        self.order_id = order_id
        self.barista_name = barista_name
        self.items = []
        self.status = "new"
        self.created_at = datetime.now().strftime("%H:%M:%S")
        self.total_amount = 0

    def add_item(self, cart_item):
        self.items.append(cart_item)
        self.total_amount += cart_item.total

    def to_dict(self):
        return {
            'order_id': self.order_id,
            'barista': self.barista_name,
            'items': [{'name': i.name, 'quantity': i.quantity, 'price': i.price} for i in self.items],
            'total': self.total_amount,
            'time': self.created_at
        }


class Shift:
    """Смена"""

    def __init__(self, barista: Barista):
        self.barista = barista

        self.start_time = datetime.now()
        self.end_time = None

        self.status = True

        self.orders: [Order] = []
        self.total_revenue = 0

    def close(self):
        self.end_time = datetime.now()

        self.status = False

        self.total_revenue = sum(order.total_amount for order in self.orders)

    def add_order(self, order):
        self.orders.append(order)

    def to_dict(self):
        duration = ""
        if self.end_time:
            duration_minutes = int((self.end_time - self.start_time).total_seconds() / 60)
            duration = f"{duration_minutes} мин"

        return {
            'barista': self.barista.name,
            'start_time': self.start_time.strftime("%H:%M"),
            'end_time': self.end_time.strftime("%H:%M") if self.end_time else "",
            'duration': duration,
            'orders_count': len(self.orders),
            'revenue': self.total_revenue,
            'status': self.status
        }
