import os
from datetime import datetime, date

from dotenv import load_dotenv
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, select, Boolean, ForeignKey, Date, func, \
    Float
from sqlalchemy.orm import sessionmaker

CAFE_ID = 2

load_dotenv()
address = os.getenv("DATABASE_ADDRESS")

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
                    .where(work_shift_table.c.close_datetime.is_not(None))
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
