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
)

order_drink_table = Table(
    "order_drink",
    metadata_obj,
    Column("order_id", Integer, ForeignKey("order.id")),
    Column("drink_id", Integer, ForeignKey("drink.id")),
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

    def get_drinks(self, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (select(
                drink_table.c.id,
                drink_table.c.category_id,
                drink_table.c.name,
                drink_table.c.price,
                drink_table.c.size,
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
    def get_all_shifts(cls, barista_id, cafe_id=CAFE_ID):
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
                    .order_by(work_shift_table.c.datetime.desc()))

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
    def close_today_shift(cls, shift_id: int, order_amount, revenue, cafe_id=CAFE_ID):
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
    def create_order(cls, shift, items: [], cafe_id=CAFE_ID):
        with Session() as session:
            total_price = sum(item.total for item in items)

            stmt_order = order_table.insert().values(
                is_free=False,
                price=total_price,
                discount_price=total_price,
                datetime=datetime.now(),
                time=datetime.now(),
                complete_time=datetime.now(),
                is_paid=True,
                in_process=True,
                is_processed=True,
                is_completed=True,
                is_thrown_out=False,
                cafe_id=cafe_id,
                shift_id=shift.shift_id,
            ).returning(order_table.c.id)

            result_order = session.execute(stmt_order)
            order_id = result_order.fetchone()[0]

            for item in items:
                stmt_order_drink = order_drink_table.insert().values(
                    order_id=order_id,
                    drink_id=item.product.drink_id,
                    amount=item.quantity
                )
                session.execute(stmt_order_drink)

            session.commit()
            return order_id

    @classmethod
    def get_orders(cls, shift_id: int, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (select(
                order_table.c.id,
                order_table.c.discount_price,
                order_table.c.datetime
            )
                    .where(order_table.c.cafe_id == cafe_id)
                    .where(order_table.c.shift_id == shift_id))

            result = session.execute(stmt)
            return result.fetchall()
