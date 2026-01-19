import datetime


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


class Order:
    """Заказ"""

    def __init__(self, order_id, barista_name):
        self.order_id = order_id
        self.barista_name = barista_name
        self.items = []
        self.status = "new"
        self.created_at = datetime.datetime.now().strftime("%H:%M:%S")
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

    def __init__(self, barista_name):
        self.barista_name = barista_name
        self.start_time = datetime.datetime.now()
        self.end_time = None
        self.orders = []
        self.total_revenue = 0
        self.status = "active"

    def close_shift(self):
        self.end_time = datetime.datetime.now()
        self.status = "closed"
        self.total_revenue = sum(order.total_amount for order in self.orders)

    def add_order(self, order):
        self.orders.append(order)

    def to_dict(self):
        duration = ""
        if self.end_time:
            duration_minutes = int((self.end_time - self.start_time).total_seconds() / 60)
            duration = f"{duration_minutes} мин"

        return {
            'barista': self.barista_name,
            'start_time': self.start_time.strftime("%H:%M"),
            'end_time': self.end_time.strftime("%H:%M") if self.end_time else "",
            'duration': duration,
            'orders_count': len(self.orders),
            'revenue': self.total_revenue,
            'status': self.status
        }
