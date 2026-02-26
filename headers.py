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
    def __init__(self, drink_id, category_id, name, size, price, calories, volume=None, visible=True):
        self._drink_id = drink_id
        self._name = name
        self._category_id = category_id
        self._size = size
        self._price = price
        self._calories = calories
        self._visible = visible

        self._size_unit = "мл" if volume else "г"

        self._drink_ingredients: [DrinkIngredient] = []

    @property
    def drink_id(self):
        return self._drink_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, price):
        self._price = price

    @property
    def calories(self):
        return self._calories

    @calories.setter
    def calories(self, calories):
        self._calories = calories

    @property
    def category_id(self):
        return self._category_id

    @property
    def size_unit(self):
        return self._size_unit

    @property
    def drink_ingredients(self):
        return self._drink_ingredients

    def add_ingredient(self, ingredient, amount):
        drink_ingredient = DrinkIngredient.insert(self, ingredient, amount)
        if drink_ingredient:
            self._drink_ingredients.append(drink_ingredient)

    def get_ingredients(self):
        if not self._drink_ingredients:
            drink_ingredients_db = database.get_drink_ingredients(self._drink_id)

            for drink_ingredient_db in drink_ingredients_db:
                drink_ingredient = DrinkIngredient(self._drink_id, drink_ingredient_db[0], drink_ingredient_db[5])
                drink_ingredient.ingredient = Ingredient(drink_ingredient_db[0], drink_ingredient_db[1], drink_ingredient_db[2],
                                                         drink_ingredient_db[3], drink_ingredient_db[4])

                self._drink_ingredients.append(drink_ingredient)

        return self._drink_ingredients

    def delete_ingredient(self, drink_ingredient):
        if drink_ingredient in self._drink_ingredients:
            if drink_ingredient.delete():
                self._drink_ingredients.remove(drink_ingredient)

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value

    def update(self):
        return DataBase.update_drink(
            drink_id=self._drink_id,
            name=self._name,
            price=self._price,
            size=self._size,
            calories=self._calories,
            visible=self._visible
        )

    def delete(self):
        if database.check_drink_in_orders(self._drink_id):
            print(f"Напиток '{self._name}' используется в заказах и не может быть удален")
            return False

        return DataBase.delete_drink(self._drink_id)

    def toggle_visibility(self):
        self._visible = not self._visible
        return self.update()

    @classmethod
    def get_by_id(cls, drink_id):
        drink_data = DataBase.get_drink_by_id(drink_id)

        if drink_data:
            cat = Category.get_by_name("Десерты")
            return cls(
                drink_id=drink_data[0],
                category_id=drink_data[1],
                name=drink_data[2],
                size=drink_data[3],
                price=drink_data[4],
                calories=drink_data[5],
                volume=not drink_data[1] == cat.category_id
            )

        return None


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
    def __init__(self, order_id=None, shift_id=None, total_price=0, drink_amount=0, created_at=None,
                 is_free=False, cafe_user_id=None):
        self._order_id = order_id
        self._shift_id = shift_id

        self._items: [CartItem] = []

        time = created_at or datetime.now()
        self._created_at = time.strftime("%H:%M:%S")

        self._total_price = total_price
        self._drink_amount = drink_amount

        self._is_free = is_free

        self._cafe_user_id = cafe_user_id

    @property
    def order_id(self):
        return self._order_id

    @property
    def cafe_user_id(self):
        return self._cafe_user_id

    @property
    def is_free(self):
        return self._is_free

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
    def total_hours(self) -> Optional[int]:
        start_time = self.start_time - timedelta(minutes=5)
        start_time = start_time.replace(minute=0, second=0) + timedelta(hours=1)

        if self.end_time:
            close_time = self.end_time.replace(minute=0, second=0)
            total_seconds = close_time.timestamp() - start_time.timestamp()

            hours = int(total_seconds // 3600)
            hours = 0 if hours < 0 else hours
            print(hours)
            return hours
        else:
            # close_time = datetime.now().replace(minute=0, second=0)
            # total_seconds = close_time.timestamp() - start_time.timestamp()
            #
            # hours = int(total_seconds // 3600)
            # hours = 0 if hours < 0 else hours
            print("None")
            return None

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
        # if self.orders:
        #     return
        self.orders = []

        orders_db = database.get_orders(self.shift_id)
        if orders_db:
            for order_data in orders_db:
                order = Order(
                    order_id=order_data[0],
                    shift_id=self.shift_id,
                    total_price=order_data[1],
                    drink_amount=order_data[2],
                    created_at=order_data[3],
                    is_free=order_data[4],
                    cafe_user_id=order_data[5],
                )

                self.orders.append(order)
                self.order_amount += 1
                self.revenue += order.total_price

    @classmethod
    def get_all_shifts(cls, barista: Barista, closed_only=True) -> [Self]:
        if closed_only:
            shifts_db = database.get_all_closed_shifts(barista_id=barista.barista_id)
        else:
            shifts_db = database.get_all_shifts(barista_id=barista.barista_id)

        if shifts_db:
            return [Shift(shift_id=shift[0], start_time=shift[1], end_time=shift[2], barista=barista,
                          order_amount=shift[3], revenue=shift[4]) for shift in shifts_db]

    def delete_order(self, order: Order):
        if database.delete_order(order.order_id):
            if order in self.orders:
                self.orders.remove(order)

                self.order_amount -= 1
                self.revenue -= order.total_price


class Ingredient:
    def __init__(self, ingredient_id, name, price, size, calories, amount=None):
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
    def size(self):
        return self._size

    @property
    def price(self):
        return self._price

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount):
        self._amount = amount

    @property
    def calories(self):
        return self._calories

    @property
    def ingredient_id(self):
        return self._ingredient_id

    def update(self):
        return database.update_ingredient(
            self._ingredient_id,
            self._name,
            self._price,
            self._size,
            self._calories,
            self._amount
        )

    def delete(self):
        drink_ingredients = database.get_drink_ingredients_by_ingredient(self._ingredient_id)

        if drink_ingredients:
            print(f"Ингредиент '{self._name}' используется в {len(drink_ingredients)} напитках")
            return False

        return database.delete_ingredient(self._ingredient_id)

    @classmethod
    def create(cls, name, price, size, calories, amount=0):
        result = database.create_ingredient(
            name=name,
            price=price,
            size=size,
            calories=calories,
            amount=amount
        )

        if result:
            return cls(
                ingredient_id=result[0],
                name=result[1],
                price=result[2],
                size=result[3],
                calories=result[4],
                amount=result[5]
            )

        return None

    def receive(self, amount, price):
        result = database.receive_ingredient(
            ingredient_id=self._ingredient_id,
            amount=amount,
            price=price
        )

        if result:
            self._amount = result[1]
            return True

        return False

    def get_receive_history(self, start_date=None, end_date=None):
        return database.get_ingredient_receives(
            ingredient_id=self._ingredient_id,
            start_date=start_date,
            end_date=end_date
        )


class DrinkIngredient:
    def __init__(self, drink_id, ingredient_id, amount):
        self._drink_id = drink_id
        self._ingredient_id = ingredient_id
        self._amount = amount

        self._drink = None
        self._ingredient = None

    @property
    def ingredient(self):
        return self._ingredient

    @ingredient.setter
    def ingredient(self, val):
        self._ingredient = val

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, val):
        self._amount = val

    @property
    def drink(self):
        return self._drink

    @drink.setter
    def drink(self, drink):
        self._drink = drink

    @classmethod
    def insert(cls, drink: Drink, ingredient: Ingredient, amount):
        res = database.add_drink_ingredient(drink.drink_id, ingredient.ingredient_id, amount)

        if res:
            drink_ingredient = DrinkIngredient(res[0], res[1], res[2])
            drink_ingredient._drink = drink
            drink_ingredient._ingredient = ingredient

            return drink_ingredient

    def update(self):
        if database.update_drink_ingredient(self.drink.drink_id, self.ingredient.ingredient_id, self.amount):
            return True

        return False

    def delete(self):
        if database.delete_drink_ingredient(self.drink.drink_id, self.ingredient.ingredient_id):
            return True

        return False
