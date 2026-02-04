from datetime import datetime, timedelta
from typing import Self, Optional

from database import DataBase

PRIMARY_COLOR = "pink"
SECONDARY_COLOR = "lavenderblush"
THIRD_COLOR = "snow"
FOURTH_COLOR = "snow"
TOP_APP_BAR_COLOR = "white"

database = DataBase()


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

    @classmethod
    def get_by_name(cls, name):
        res = database.get_category_by_name(name)
        if res:
            return Category(res[0], res[1])


class Drink:
    def __init__(self, drink_id, category_id, name, prices, sizes, calories, sizes_label=None, volume=None):
        self._drink_id = drink_id
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
    def drink_id(self):
        return self._drink_id

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


class Menu:
    def __init__(self):
        self.categories: [Category] = None

        self.drinks: [Drink] = None

        self.get_categories()
        self.get_drinks()

    def get_categories(self):
        categories_db = database.get_categories()
        if categories_db:
            self.categories = [Category(category[0], category[1]) for category in categories_db]

    def get_drinks(self):
        drinks_db = database.get_drinks()

        if drinks_db:
            self.drinks = []

            cat = next((cat for cat in self.categories if cat.name == "Десерты"), None)

            for drink_db in drinks_db:
                drink = next((drink for drink in self.drinks if drink.name == drink_db[2]), None)

                if drink:
                    drink._sizes.append(drink_db[4])
                    drink._prices.append(drink_db[3])
                    drink._calories.append(drink_db[5])
                else:
                    self.drinks.append(
                        Drink(drink_db[0], drink_db[1], drink_db[2], [drink_db[3]], [drink_db[4]], [drink_db[5]],
                              sizes_label=["M", "L"], volume=not drink_db[1] == cat.category_id))


class Barista:
    def __init__(self, barista_id, name):
        self._barista_id = barista_id
        self._name = name

        self._is_admin = False

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

    @property
    def is_admin(self):
        return self._is_admin

    @is_admin.setter
    def is_admin(self, is_admin):
        self._is_admin = is_admin

    @classmethod
    def get_all_baristas(cls) -> [Self]:
        baristas_db = database.get_baristas()

        baristas = []
        for barista in baristas_db:
            baristas.append(Barista(barista[4], barista[3]))

        return baristas


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

    def add(self, product: Drink, size):
        cart_item = next((cart_item for cart_item in self.cart_items if
                          cart_item.product.drink_id == product.drink_id and
                          cart_item.size == size), None)

        if cart_item:
            cart_item.quantity += 1
        else:
            self.cart_items.append(CartItem(product, size))

    def pop(self, product: Drink, size):
        cart_item = next((cart_item for cart_item in self.cart_items if
                          cart_item.product.drink_id == product.drink_id and
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

    def __init__(self, order_id=None, shift_id=None, total_price=0, drink_amount=0, created_at=None):
        self.order_id = order_id

        self.shift_id = shift_id

        self._items: [CartItem] = []

        time = created_at or datetime.now()
        self.created_at = time.strftime("%H:%M:%S")

        self.total_price = total_price
        self.drink_amount = drink_amount

    def add_item(self, cart_item: CartItem):
        self._items.append(cart_item)

        self.total_price += cart_item.total
        self.drink_amount += cart_item.quantity

    @property
    def items(self):
        if not self._items:
            self.get_items()

        return self._items

    def get_items(self):
        items_db = database.get_items(self.order_id)
        if items_db:
            category = Category.get_by_name("Десерты")
            self.total_price = 0
            self.drink_amount = 0

            for item in items_db:
                self.add_item(
                    CartItem(
                        product=Drink(drink_id=item[0], category_id=item[1], name=item[2],
                                      prices=[item[3]], sizes=[item[4]], calories=[item[5]],
                                      sizes_label=None, volume=category.category_id != item[1]),
                        size=item[4],
                        quantity=item[6]
                    )
                )


class Shift:
    def __init__(self, shift_id=None, start_time=None, end_time=None, barista=None, order_amount=0, revenue=0):
        self.shift_id = shift_id

        self.start_time = start_time
        self.end_time = end_time

        self.barista: Optional[Barista] = barista

        self.order_amount = order_amount
        self.revenue = revenue

        self.orders: [Order] = []

        self.is_active = False

    def reset(self):
        self.shift_id = None

        self.start_time = None
        self.end_time = None

        self.barista: Optional[Barista] = None

        self.order_amount = 0
        self.revenue = 0

        self.orders: [Order] = []

        self.is_active = False

    @property
    def total_hours(self) -> int:
        start_time = self.start_time - timedelta(minutes=5)
        start_time = start_time.replace(minute=0, second=0) + timedelta(hours=1)

        if self.end_time:
            close_time = self.end_time.replace(minute=0, second=0)
            total_seconds = close_time.timestamp() - start_time.timestamp()
        else:
            close_time = datetime.now().replace(minute=0, second=0)
            total_seconds = close_time.timestamp() - start_time.timestamp()

        hours = int(total_seconds // 3600)
        hours = 0 if hours < 0 else hours
        return hours

    def open(self, barista: Barista):
        res = database.open_shift(cafe_user_id=barista.barista_id)

        if res:
            self.shift_id = res.id
            self.start_time = res.datetime

            self.barista = barista

            self.is_active = True

    def close(self):
        res = database.close_shift(shift_id=self.shift_id, order_amount=self.order_amount, revenue=self.revenue)

        if res:
            self.reset()

    @classmethod
    def delete(cls, shift):
        res = database.delete_shift(shift_id=shift.shift_id)
        if res:
            return True

    def add_order(self, order: Order):
        order_id_db = database.create_order(self.shift_id, order)

        if order_id_db:
            order.order_id = order_id_db
            self.orders.append(order)

            self.order_amount += 1
            self.revenue += order.total_price

    def get_today_shift(self):
        shift_db = database.get_today_open_shift()

        if shift_db:
            self.shift_id = shift_db[0]
            self.start_time = shift_db[1]
            self.end_time = shift_db[2]

            self.barista = Barista(shift_db[4], shift_db[3])

            self.is_active = True

            self.get_orders()

    def get_orders(self):
        if self.orders:
            return

        orders_db = database.get_orders(self.shift_id)
        if orders_db:
            for order_data in orders_db:
                order = Order(
                    order_id=order_data[0],
                    shift_id=self.shift_id,
                    total_price=order_data[1],
                    drink_amount=order_data[2],
                    created_at=order_data[3]
                )

                self.orders.append(order)
                self.order_amount += 1
                self.revenue += order.total_price

    @classmethod
    def get_all_shifts(cls, barista: Barista) -> [Self]:
        shifts_db = database.get_all_shifts(barista_id=barista.barista_id)
        return [Shift(shift_id=shift[0], start_time=shift[1], end_time=shift[2], barista=barista,
                      order_amount=shift[3], revenue=shift[4]) for shift in shifts_db]

    def delete_order(self, order: Order):
        if database.delete_order(order.order_id):
            if order in self.orders:
                self.orders.remove(order)

                self.order_amount -= 1
                self.revenue -= order.total_price


class Ingredient:
    def __init__(self, ingredient_id, name, price, size, calories, amount):
        self._ingredient_id = ingredient_id
        self._name = name
        self._price = price
        self._size = size
        self._calories = calories
        self._amount = amount

    @classmethod
    def get_all(cls):
        ingredients_db = database.get_all_ingredients()
        if ingredients_db:
            return [Ingredient(ingredient_db[0], ingredient_db[1], ingredient_db[2], ingredient_db[3], ingredient_db[4],
                               ingredient_db[5]) for ingredient_db in ingredients_db]

    @property
    def name(self):
        return self._name

    @property
    def amount(self):
        return self._amount
