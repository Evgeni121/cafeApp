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
    def __init__(self, drink_id, category_id, name, size, price, calories, volume=None):
        self._drink_id = drink_id
        self._name = name
        self._category_id = category_id
        self._size = size
        self._price = price
        self._calories = calories

        self._size_unit = "мл" if volume else "г"

        self.ingredients: [DrinkIngredient] = []

    @property
    def drink_id(self):
        return self._drink_id

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    @property
    def price(self):
        return self._price

    @property
    def calories(self):
        return self._calories

    @property
    def category_id(self):
        return self._category_id

    @property
    def size_unit(self):
        return self._size_unit


class MenuDrink:
    def __init__(self, drinks: [Drink], category_id, name):
        self._drinks: [Drink] = drinks

        self._category_id = category_id
        self._name = name

        self._selected_drink = None

    @property
    def drink_id(self):
        return self.selected_drink.drink_id

    @property
    def name(self):
        return self._name

    @property
    def category_id(self):
        return self._category_id

    @property
    def drinks(self):
        return self._drinks

    @property
    def selected_drink(self):
        if not self._selected_drink:
            self._selected_drink = sorted(self._drinks, key=lambda x: x.size)[0]

        return self._selected_drink

    @selected_drink.setter
    def selected_drink(self, selected_drink: Drink):
        self._selected_drink = selected_drink

    def add_drink(self, drink: Drink):
        self._drinks.append(drink)


class Menu:
    def __init__(self):
        self._categories: [Category] = None

        self._menu_drinks: [MenuDrink] = None

        self.get_categories()
        self.get_drinks()

    @property
    def categories(self):
        return self._categories

    @property
    def menu_drinks(self):
        return self._menu_drinks

    def get_categories(self):
        categories_db = database.get_categories()
        if categories_db:
            self._categories = [Category(category[0], category[1]) for category in categories_db]

    def get_drinks(self):
        drinks_db = database.get_drinks()

        if drinks_db:
            self._menu_drinks = []

            cat = next((cat for cat in self.categories if cat.name == "Десерты"), None)

            for drink_db in drinks_db:
                menu_drink = next((drink for drink in self.menu_drinks if drink.name == drink_db[2]), None)

                drink = Drink(drink_db[0], drink_db[1], drink_db[2], drink_db[3], drink_db[4], drink_db[5],
                              volume=not drink_db[1] == cat.category_id)

                if menu_drink:
                    menu_drink.add_drink(drink)
                else:
                    self.menu_drinks.append(MenuDrink([drink], drink_db[1], drink_db[2]))


class Barista:
    def __init__(self, barista_id=None, name=None):
        self._barista_id = barista_id
        self._name = name

        self._is_admin = False

    @property
    def barista_id(self):
        return self._barista_id

    @property
    def name(self):
        return self._name

    @property
    def is_admin(self):
        return self._is_admin

    @classmethod
    def get_all_baristas(cls) -> [Self]:
        baristas_db = database.get_baristas()

        baristas = []
        for barista in baristas_db:
            baristas.append(Barista(barista[4], barista[3]))

        return baristas

    @classmethod
    def create(cls, name) -> Self:
        barista_bd = database.add_barista(name)
        if barista_bd:
            return Barista(barista_id=barista_bd[0], name=barista_bd[1])


class CartItem:
    def __init__(self, drink: Drink, quantity=1):
        self._drink: Drink = drink
        self._quantity = quantity

    @property
    def drink(self):
        return self._drink

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, val):
        self._quantity = val

    @property
    def total_price(self):
        return self._drink.price * self._quantity


class Cart:
    def __init__(self):
        self._cart_items: [CartItem] = []

    @property
    def cart_items(self):
        return self._cart_items

    def add_drink(self, drink: Drink):
        cart_item = next((cart_item for cart_item in self._cart_items if cart_item.drink.drink_id == drink.drink_id), None)

        if cart_item:
            cart_item.quantity += 1
        else:
            self._cart_items.append(CartItem(drink))

    def pop_drink(self, drink: Drink):
        cart_item = next((cart_item for cart_item in self._cart_items if cart_item.drink.drink_id == drink.drink_id), None)

        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
            else:
                self._cart_items.remove(cart_item)

    @property
    def total_price(self):
        return sum(lambda x: item.total_price for item in self._cart_items)

    def clear(self):
        self._cart_items.clear()


class Order:
    def __init__(self, order_id=None, shift_id=None, total_price=0, drink_amount=0, created_at=None):
        self._order_id = order_id
        self._shift_id = shift_id

        self._items: [CartItem] = []

        time = created_at or datetime.now()
        self._created_at = time.strftime("%H:%M:%S")

        self._total_price = total_price
        self._drink_amount = drink_amount

    @property
    def order_id(self):
        return self._order_id

    @order_id.setter
    def order_id(self, order_id):
        self._order_id = order_id

    @property
    def total_price(self):
        return self._total_price

    @property
    def created_at(self):
        return self._created_at

    @property
    def drink_amount(self):
        return self._drink_amount

    def add_item(self, cart_item: CartItem):
        self._items.append(cart_item)

        self._total_price += cart_item.total_price
        self._drink_amount += cart_item.quantity

    @property
    def items(self):
        if not self._items:
            self.get_items()

        return self._items

    def get_items(self):
        items_db = database.get_items(self._order_id)
        if items_db:
            cat = Category.get_by_name("Десерты")
            self._total_price = 0
            self._drink_amount = 0

            for item in items_db:
                drink = Drink(item[0], item[1], item[2], item[3], item[4], item[5],
                              volume=not item[1] == cat.category_id)

                self.add_item(CartItem(drink, quantity=item[6]))


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


class DrinkIngredient:
    def __init__(self, drink_id, ingredient_id, amount):
        self._drink_id = drink_id
        self._ingredient_id = ingredient_id
        self._amount = amount
