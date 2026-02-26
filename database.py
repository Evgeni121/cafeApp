import os
from datetime import datetime, date

from dotenv import load_dotenv
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, select, Boolean, ForeignKey, Date, func, \
    Float, DateTime
from sqlalchemy.orm import sessionmaker

CAFE_ID = 2

load_dotenv()
# address = os.getenv("DATABASE_ADDRESS")
address = os.environ.get('DATABASE_ADDRESS')

if not address:
    raise "Get DATABASE_ADDRESS error!"

engine = create_engine(f"{address}/postgres", echo=False)
Session = sessionmaker(engine, expire_on_commit=False)

metadata_obj = MetaData()

user_table = Table(
    "user",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("telegram_id", Integer),
    Column("username", String),
    Column("first_name", String),
)

cafe_user_table = Table(
    "cafe_user",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("cafe_id", Integer),
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("is_barista", Boolean),
    Column("is_main_barista", Boolean)
)

work_shift_table = Table(
    "work_shift",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("cafe_id", Integer),
    Column("cafe_user_id", Integer, ForeignKey("cafe_user.id")),
    Column("datetime", Date),
    Column("close_datetime", Date),
    Column("is_paid", Boolean),
    Column("order_amount", Integer),
    Column("revenue", Integer),
)

category_table = Table(
    "category",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String),
)

drink_table = Table(
    "drink",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("cafe_id", Integer),
    Column("category_id", Integer, ForeignKey("category.id")),
    Column("name", String),
    Column("price", Float),
    Column("size", Integer),
    Column("calories", Integer),
    Column("visible", Boolean),
)

order_table = Table(
    "order",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("cafe_user_id", Integer, ForeignKey("cafe_user.id")),
    Column("is_free", Boolean),
    Column("is_paid", Boolean),
    Column("in_process", Boolean),
    Column("is_processed", Boolean),
    Column("is_completed", Boolean),
    Column("is_thrown_out", Boolean),
    Column("datetime", Date),
    Column("time", Date),
    Column("complete_time", Date),
    Column("price", Float),
    Column("cafe_id", Integer),
    Column("discount", Float),
    Column("discount_price", Float),
    Column("shift_id", Integer, ForeignKey("work_shift.id")),
    Column("drink_amount", Integer),
)

order_drink_table = Table(
    "order_drink",
    metadata_obj,
    Column("order_id", Integer, ForeignKey("order.id")),
    Column("drink_id", Integer, ForeignKey("drink.id")),
    Column("amount", Integer),
)

ingredient_table = Table(
    "ingredient",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("cafe_id", Integer, ForeignKey("cafe.id")),
    Column("name", String),
    Column("price", Float),
    Column("size", Integer),
    Column("calories", Integer),
    Column("amount", Integer),
)

drink_ingredient_table = Table(
    "drink_ingredient",
    metadata_obj,
    Column("drink_id", Integer, ForeignKey("drink.id")),
    Column("ingredient_id", Integer, ForeignKey("ingredient.id")),
    Column("amount", Integer, ForeignKey("amount")),
)

ingredient_receive_table = Table(
    "ingredient_receive",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("ingredient_id", Integer, ForeignKey("ingredient.id")),
    Column("amount", Integer, ForeignKey("amount")),
    Column("date", DateTime),
    Column("price", Float),
)


class DataBase:
    def __init__(self):
        pass

    def get_categories(self):
        with Session() as session:
            stmt = (select(
                category_table.c.id,
                category_table.c.name,
            )
                    .select_from(
                category_table
            )
                    .order_by(category_table.c.name)
                    )

            result = session.execute(stmt)
            return result.fetchall()

    def get_category_by_name(self, name):
        with Session() as session:
            stmt = (select(
                category_table.c.id,
                category_table.c.name,
            )
                    .select_from(
                category_table
            )
                    .where(category_table.c.name == name)
                    )

            result = session.execute(stmt)
            return result.first()

    def get_drinks(self, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (select(
                drink_table.c.id,
                drink_table.c.category_id,
                drink_table.c.name,
                drink_table.c.size,
                drink_table.c.price,
                drink_table.c.calories,
            )
                    .select_from(
                drink_table
            )
                    .where(drink_table.c.cafe_id == cafe_id)
                    .where(drink_table.c.visible.is_(True))
                    .order_by(drink_table.c.name))

            result = session.execute(stmt)
            return result.fetchall()

    @classmethod
    def get_baristas(cls, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (select(
                user_table.c.id,
                user_table.c.telegram_id,
                user_table.c.username,
                user_table.c.first_name,
                cafe_user_table.c.id,
                cafe_user_table.c.cafe_id,
                cafe_user_table.c.is_barista
            )
                    .select_from(
                cafe_user_table.join(
                    user_table,
                    cafe_user_table.c.user_id == user_table.c.id
                )
            )
                    .where(cafe_user_table.c.cafe_id == cafe_id)
                    .where(cafe_user_table.c.is_barista.is_(True))
                    .where(cafe_user_table.c.is_main_barista.is_(False)))

            result = session.execute(stmt)
            return result.fetchall()

    @classmethod
    def get_today_open_shift(cls, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (select(
                work_shift_table.c.id,
                work_shift_table.c.datetime,
                work_shift_table.c.close_datetime,
                user_table.c.first_name,
                cafe_user_table.c.id,
            )
                    .join(cafe_user_table, work_shift_table.c.cafe_user_id == cafe_user_table.c.id)
                    .join(user_table, cafe_user_table.c.user_id == user_table.c.id)
                    .where(work_shift_table.c.cafe_id == cafe_id)
                    .where(func.date(work_shift_table.c.datetime) == date.today())
                    .where(work_shift_table.c.close_datetime.is_(None)))

            result = session.execute(stmt)
            return result.first()

    @classmethod
    def get_all_closed_shifts(cls, barista_id: int, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (select(
                work_shift_table.c.id,
                work_shift_table.c.datetime,
                work_shift_table.c.close_datetime,
                work_shift_table.c.order_amount,
                work_shift_table.c.revenue,
            )
                    .join(cafe_user_table, work_shift_table.c.cafe_user_id == cafe_user_table.c.id)
                    .join(user_table, cafe_user_table.c.user_id == user_table.c.id)
                    .where(work_shift_table.c.cafe_id == cafe_id)
                    .where(work_shift_table.c.cafe_user_id == barista_id)
                    .where(work_shift_table.c.is_paid.is_(False))
                    .where(work_shift_table.c.close_datetime.is_not(None))
                    .order_by(work_shift_table.c.datetime))

            result = session.execute(stmt)
            return result.fetchall()

    @classmethod
    def get_all_shifts(cls, barista_id: int, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (select(
                work_shift_table.c.id,
                work_shift_table.c.datetime,
                work_shift_table.c.close_datetime,
                work_shift_table.c.order_amount,
                work_shift_table.c.revenue,
            )
                    .join(cafe_user_table, work_shift_table.c.cafe_user_id == cafe_user_table.c.id)
                    .join(user_table, cafe_user_table.c.user_id == user_table.c.id)
                    .where(work_shift_table.c.cafe_id == cafe_id)
                    .where(work_shift_table.c.cafe_user_id == barista_id)
                    .where(work_shift_table.c.is_paid.is_(False))
                    .order_by(work_shift_table.c.datetime))

            result = session.execute(stmt)
            return result.fetchall()

    @classmethod
    def open_shift(cls, cafe_user_id, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = work_shift_table.insert().values(
                cafe_id=cafe_id,
                cafe_user_id=cafe_user_id,
                datetime=datetime.now(),
                is_paid=False
            ).returning(work_shift_table.c.id, work_shift_table.c.datetime)

            try:
                result = session.execute(stmt)
                session.commit()
                return result.fetchone()
            except Exception as e:
                session.rollback()
                print(e)
                return None

    @classmethod
    def close_shift(cls, shift_id: int, order_amount, revenue, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (work_shift_table.update()
                    .where(work_shift_table.c.id == shift_id)
                    .where(work_shift_table.c.cafe_id == cafe_id)
                    .where(work_shift_table.c.close_datetime.is_(None))
                    .values(close_datetime=datetime.now(), order_amount=order_amount, revenue=revenue))

            result = session.execute(stmt)
            session.commit()
            return result.rowcount > 0

    @classmethod
    def create_order(cls, shift_id, order, cafe_id=CAFE_ID):
        with Session() as session:
            stmt_order = order_table.insert().values(
                is_free=False,
                price=order.total_price,
                discount_price=order.total_price,
                datetime=datetime.now(),
                time=datetime.now(),
                complete_time=datetime.now(),
                is_paid=True,
                in_process=True,
                is_processed=True,
                is_completed=True,
                is_thrown_out=False,
                cafe_id=cafe_id,
                shift_id=shift_id,
                drink_amount=order.drink_amount
            ).returning(order_table.c.id)

            result_order = session.execute(stmt_order)
            order_id = result_order.fetchone()[0]

            for item in order.items:
                stmt_order_drink = order_drink_table.insert().values(
                    order_id=order_id,
                    drink_id=item.drink.drink_id,
                    amount=item.quantity
                )
                session.execute(stmt_order_drink)

            session.commit()
            return order_id

    @classmethod
    def delete_order(cls, order_id: int, cafe_id=CAFE_ID):
        with Session() as session:
            stmt_delete_drinks = order_drink_table.delete().where(
                order_drink_table.c.order_id == order_id
            )
            session.execute(stmt_delete_drinks)

            stmt_delete_order = order_table.delete().where(
                order_table.c.id == order_id,
                order_table.c.cafe_id == cafe_id
            )

            result = session.execute(stmt_delete_order)
            session.commit()
            return result.rowcount > 0

    @classmethod
    def get_orders(cls, shift_id: int, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (select(
                order_table.c.id,
                order_table.c.discount_price,
                order_table.c.drink_amount,
                order_table.c.datetime,
                order_table.c.is_free,
                order_table.c.cafe_user_id
            )
                    .select_from(
                order_table
            )
                    .where(order_table.c.cafe_id == cafe_id)
                    .where(order_table.c.shift_id == shift_id)
                    .order_by(order_table.c.id))

            return session.execute(stmt).fetchall()

    @classmethod
    def get_items(cls, order_id: int, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (select(
                drink_table.c.id,
                drink_table.c.category_id,
                drink_table.c.name,
                drink_table.c.size,
                drink_table.c.price,
                drink_table.c.calories,
                order_drink_table.c.amount,
            )
                    .select_from(
                drink_table.join(order_drink_table, order_drink_table.c.drink_id == drink_table.c.id)
            )
                    .where(order_drink_table.c.order_id == order_id)
                    .where(drink_table.c.cafe_id == cafe_id))

            return session.execute(stmt).fetchall()

    @classmethod
    def delete_shift(cls, shift_id: int, cafe_id=CAFE_ID):
        with Session() as session:
            # 1. Находим все заказы этой смены
            orders_stmt = select(order_table.c.id).where(
                order_table.c.shift_id == shift_id,
                order_table.c.cafe_id == cafe_id
            )
            orders = session.execute(orders_stmt).fetchall()
            order_ids = [order.id for order in orders]

            if order_ids:
                # 2. Удаляем напитки из заказов
                delete_drinks_stmt = order_drink_table.delete().where(
                    order_drink_table.c.order_id.in_(order_ids)
                )
                session.execute(delete_drinks_stmt)

                # 3. Удаляем заказы
                delete_orders_stmt = order_table.delete().where(
                    order_table.c.id.in_(order_ids)
                )
                session.execute(delete_orders_stmt)

            # 4. Удаляем смену
            delete_shift_stmt = work_shift_table.delete().where(
                work_shift_table.c.id == shift_id,
                work_shift_table.c.cafe_id == cafe_id
            )

            result = session.execute(delete_shift_stmt)
            session.commit()
            return result.rowcount > 0

    @classmethod
    def get_all_ingredients(cls, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (select(
                ingredient_table.c.id,
                ingredient_table.c.name,
                ingredient_table.c.price,
                ingredient_table.c.size,
                ingredient_table.c.calories,
                ingredient_table.c.amount,
            )
                    .where(ingredient_table.c.cafe_id == cafe_id)
                    .order_by(ingredient_table.c.name))

            result = session.execute(stmt)
            return result.fetchall()

    @classmethod
    def add_barista(cls, name, cafe_id=CAFE_ID):
        pass

    @classmethod
    def add_drink_ingredient(cls, drink_id, ingredient_id, amount):
        with Session() as session:
            try:
                stmt = drink_ingredient_table.insert().values(
                    drink_id=drink_id,
                    ingredient_id=ingredient_id,
                    amount=amount
                ).returning(
                    drink_ingredient_table.c.drink_id,
                    drink_ingredient_table.c.ingredient_id,
                    drink_ingredient_table.c.amount
                )
                result = session.execute(stmt)
                session.commit()
                return result.fetchone()
            except Exception as e:
                session.rollback()
                print(f"Ошибка при добавлении ингредиента к напитку: {e}")
                return None

    @classmethod
    def get_drink_ingredients(cls, drink_id, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (select(
                ingredient_table.c.id,
                ingredient_table.c.name,
                ingredient_table.c.price,
                ingredient_table.c.size,
                ingredient_table.c.calories,
                drink_ingredient_table.c.amount,
            )
                    .select_from(
                drink_ingredient_table.join(
                    ingredient_table,
                    drink_ingredient_table.c.ingredient_id == ingredient_table.c.id
                )
            )
                    .where(drink_ingredient_table.c.drink_id == drink_id)
                    .where(ingredient_table.c.cafe_id == cafe_id)
                    .order_by(ingredient_table.c.name))

            result = session.execute(stmt)
            return result.fetchall()

    @classmethod
    def update_drink_ingredient(cls, drink_id, ingredient_id, amount):
        with Session() as session:
            try:
                stmt = drink_ingredient_table.update().values(
                    amount=amount
                ).where(
                    drink_ingredient_table.c.drink_id == drink_id,
                    drink_ingredient_table.c.ingredient_id == ingredient_id
                ).returning(
                    drink_ingredient_table.c.drink_id,
                    drink_ingredient_table.c.ingredient_id,
                    drink_ingredient_table.c.amount
                )
                result = session.execute(stmt)
                session.commit()
                return result.fetchone()
            except Exception as e:
                session.rollback()
                print(f"Ошибка при обновлении ингредиента в напитке: {e}")
                return None

    @classmethod
    def delete_drink_ingredient(cls, drink_id, ingredient_id):
        with Session() as session:
            try:
                stmt = drink_ingredient_table.delete().where(
                    drink_ingredient_table.c.drink_id == drink_id,
                    drink_ingredient_table.c.ingredient_id == ingredient_id
                )

                result = session.execute(stmt)
                session.commit()

                return result.rowcount > 0

            except Exception as e:
                session.rollback()
                print(f"Ошибка при удалении ингредиента из напитка: {e}")
                return False

    @classmethod
    def update_ingredient(cls, ingredient_id, name, price, size, calories, amount, cafe_id=CAFE_ID):
        with Session() as session:
            try:
                # Проверяем, существует ли ингредиент
                check_stmt = select(ingredient_table).where(
                    ingredient_table.c.id == ingredient_id,
                    ingredient_table.c.cafe_id == cafe_id
                )
                exists = session.execute(check_stmt).first()

                if not exists:
                    print(f"Ингредиент с ID {ingredient_id} не найден")
                    return False

                # Обновляем ингредиент
                stmt = ingredient_table.update().values(
                    name=name,
                    price=price,
                    size=size,
                    calories=calories,
                    amount=amount
                ).where(
                    ingredient_table.c.id == ingredient_id,
                    ingredient_table.c.cafe_id == cafe_id
                )

                result = session.execute(stmt)
                session.commit()

                return result.rowcount > 0

            except Exception as e:
                session.rollback()
                print(f"Ошибка при обновлении ингредиента: {e}")
                return False

    @classmethod
    def get_drink_ingredients_by_ingredient(cls, ingredient_id, cafe_id=CAFE_ID):
        with Session() as session:
            try:
                stmt = (select(
                    drink_ingredient_table.c.drink_id,
                    drink_ingredient_table.c.amount,
                    drink_table.c.name,
                    drink_table.c.cafe_id
                )
                        .select_from(
                    drink_ingredient_table.join(
                        drink_table,
                        drink_ingredient_table.c.drink_id == drink_table.c.id
                    )
                )
                        .where(drink_ingredient_table.c.ingredient_id == ingredient_id)
                        .where(drink_table.c.cafe_id == cafe_id))

                result = session.execute(stmt)
                return result.fetchall()

            except Exception as e:
                print(f"Ошибка при проверке использования ингредиента: {e}")
                return []

    @classmethod
    def delete_ingredient(cls, ingredient_id, cafe_id=CAFE_ID):
        with Session() as session:
            try:
                # Проверяем, используется ли ингредиент в напитках
                check_stmt = select(drink_ingredient_table).where(
                    drink_ingredient_table.c.ingredient_id == ingredient_id
                )
                used_in_drinks = session.execute(check_stmt).first()

                if used_in_drinks:
                    print(f"Ингредиент с ID {ingredient_id} используется в напитках и не может быть удален")
                    return False

                # Удаляем ингредиент
                stmt = ingredient_table.delete().where(
                    ingredient_table.c.id == ingredient_id,
                    ingredient_table.c.cafe_id == cafe_id
                )

                result = session.execute(stmt)
                session.commit()

                return result.rowcount > 0

            except Exception as e:
                session.rollback()
                print(f"Ошибка при удалении ингредиента: {e}")
                return False

    @classmethod
    def create_ingredient(cls, name, price, size, calories, amount=0, cafe_id=CAFE_ID):
        with Session() as session:
            try:
                stmt = ingredient_table.insert().values(
                    cafe_id=cafe_id,
                    name=name,
                    price=price,
                    size=size,
                    calories=calories,
                    amount=amount
                ).returning(
                    ingredient_table.c.id,
                    ingredient_table.c.name,
                    ingredient_table.c.price,
                    ingredient_table.c.size,
                    ingredient_table.c.calories,
                    ingredient_table.c.amount
                )

                result = session.execute(stmt)
                session.commit()

                return result.fetchone()

            except Exception as e:
                session.rollback()
                print(f"Ошибка при создании ингредиента: {e}")
                return None

    @classmethod
    def receive_ingredient(cls, ingredient_id, amount, price, cafe_id=CAFE_ID):
        with Session() as session:
            try:
                select_stmt = select(ingredient_table.c.amount).where(
                    ingredient_table.c.id == ingredient_id,
                    ingredient_table.c.cafe_id == cafe_id
                )
                current_amount = session.execute(select_stmt).scalar()

                if current_amount is None:
                    print(f"Ингредиент с ID {ingredient_id} не найден")
                    return None

                # 2. Обновляем количество ингредиента
                new_amount = current_amount + amount

                update_stmt = ingredient_table.update().values(
                    amount=new_amount
                ).where(
                    ingredient_table.c.id == ingredient_id,
                    ingredient_table.c.cafe_id == cafe_id
                )
                session.execute(update_stmt)

                # 3. Создаем запись о поступлении
                insert_stmt = ingredient_receive_table.insert().values(
                    ingredient_id=ingredient_id,
                    amount=amount,
                    date=datetime.now(),
                    price=price
                ).returning(
                    ingredient_receive_table.c.id
                )

                result = session.execute(insert_stmt)
                receive_id = result.fetchone()[0]

                # Фиксируем транзакцию
                session.commit()

                return (ingredient_id, new_amount, receive_id)

            except Exception as e:
                session.rollback()
                print(f"Ошибка при добавлении поступления ингредиента: {e}")
                return None

    @classmethod
    def get_ingredient_receives(cls, ingredient_id=None, start_date=None, end_date=None, cafe_id=CAFE_ID):
        with Session() as session:
            try:
                stmt = (select(
                    ingredient_receive_table.c.id,
                    ingredient_receive_table.c.ingredient_id,
                    ingredient_receive_table.c.amount,
                    ingredient_receive_table.c.date,
                    ingredient_receive_table.c.price,
                    ingredient_table.c.name,
                    ingredient_table.c.cafe_id
                )
                        .select_from(
                    ingredient_receive_table.join(
                        ingredient_table,
                        ingredient_receive_table.c.ingredient_id == ingredient_table.c.id
                    )
                )
                        .where(ingredient_table.c.cafe_id == cafe_id))

                if ingredient_id:
                    stmt = stmt.where(ingredient_receive_table.c.ingredient_id == ingredient_id)

                if start_date:
                    stmt = stmt.where(ingredient_receive_table.c.date >= start_date)

                if end_date:
                    stmt = stmt.where(ingredient_receive_table.c.date <= end_date)

                stmt = stmt.order_by(ingredient_receive_table.c.date.desc())

                result = session.execute(stmt)
                return result.fetchall()

            except Exception as e:
                print(f"Ошибка при получении истории поступлений: {e}")
                return []

    @classmethod
    def update_drink(cls, drink_id, name, price, size, calories, visible=None, cafe_id=CAFE_ID):
        with Session() as session:
            try:
                # Проверяем существование напитка
                check_stmt = select(drink_table).where(
                    drink_table.c.id == drink_id,
                    drink_table.c.cafe_id == cafe_id
                )
                exists = session.execute(check_stmt).first()

                if not exists:
                    print(f"Напиток с ID {drink_id} не найден")
                    return False

                # Подготавливаем данные для обновления
                update_values = {}
                if name:
                    update_values['name'] = name
                if price:
                    update_values['price'] = price
                if size:
                    update_values['size'] = size
                if calories:
                    update_values['calories'] = calories
                if visible is not None:
                    update_values['visible'] = visible

                # Обновляем напиток
                stmt = drink_table.update().values(
                    **update_values
                ).where(
                    drink_table.c.id == drink_id,
                    drink_table.c.cafe_id == cafe_id
                )

                result = session.execute(stmt)
                session.commit()

                return result.rowcount > 0

            except Exception as e:
                session.rollback()
                print(f"Ошибка при обновлении напитка: {e}")
                return False

    @classmethod
    def get_drink_by_id(cls, drink_id, cafe_id=CAFE_ID):
        """
        Получить напиток по ID

        Args:
            drink_id: ID напитка
            cafe_id: ID кафе

        Returns:
            tuple: (id, category_id, name, size, price, calories) или None
        """
        with Session() as session:
            try:
                stmt = (select(
                    drink_table.c.id,
                    drink_table.c.category_id,
                    drink_table.c.name,
                    drink_table.c.size,
                    drink_table.c.price,
                    drink_table.c.calories,
                    drink_table.c.visible
                )
                        .where(drink_table.c.id == drink_id)
                        .where(drink_table.c.cafe_id == cafe_id))

                result = session.execute(stmt)
                return result.first()

            except Exception as e:
                print(f"Ошибка при получении напитка: {e}")
                return None

    @classmethod
    def delete_drink(cls, drink_id, cafe_id=CAFE_ID):
        """
        Удалить напиток

        Args:
            drink_id: ID напитка
            cafe_id: ID кафе

        Returns:
            bool: True если удаление успешно
        """
        with Session() as session:
            try:
                # Проверяем, есть ли заказы с этим напитком
                check_orders_stmt = select(order_drink_table).where(
                    order_drink_table.c.drink_id == drink_id
                )
                used_in_orders = session.execute(check_orders_stmt).first()

                if used_in_orders:
                    print(f"Напиток с ID {drink_id} используется в заказах и не может быть удален")
                    return False

                # Удаляем связи с ингредиентами
                delete_ingredients_stmt = drink_ingredient_table.delete().where(
                    drink_ingredient_table.c.drink_id == drink_id
                )
                session.execute(delete_ingredients_stmt)

                # Удаляем напиток
                stmt = drink_table.delete().where(
                    drink_table.c.id == drink_id,
                    drink_table.c.cafe_id == cafe_id
                )

                result = session.execute(stmt)
                session.commit()

                return result.rowcount > 0

            except Exception as e:
                session.rollback()
                print(f"Ошибка при удалении напитка: {e}")
                return False

    @classmethod
    def check_drink_in_orders(cls, drink_id, cafe_id=CAFE_ID):
        with Session() as session:
            try:
                stmt = (select(order_drink_table)
                        .join(drink_table, order_drink_table.c.drink_id == drink_table.c.id)
                        .where(order_drink_table.c.drink_id == drink_id)
                        .where(drink_table.c.cafe_id == cafe_id)
                        .limit(1))

                result = session.execute(stmt).first()
                return result is not None

            except Exception as e:
                print(f"Ошибка при проверке использования напитка: {e}")
                return False
