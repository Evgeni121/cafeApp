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
                    .where(drink_table.c.visible.is_(True)))

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
    def close_today_shift(cls, shift_id: int, cafe_id=CAFE_ID):
        with Session() as session:
            stmt = (work_shift_table.update()
                    .where(work_shift_table.c.id == shift_id)
                    .where(work_shift_table.c.cafe_id == cafe_id)
                    .where(work_shift_table.c.close_datetime.is_(None))
                    .values(close_datetime=datetime.now()))

            result = session.execute(stmt)
            session.commit()
            return result.rowcount > 0

    @classmethod
    def create_order(cls, shift, drinks: [], cafe_id=CAFE_ID):
        with Session() as session:
            stmt = work_shift_table.insert().values(
                cafe_id=cafe_id,
                cafe_user_id=shift.barista.barista_id,
                datetime=datetime.now(),
            ).returning(work_shift_table.c.id, work_shift_table.c.datetime)

            try:
                result = session.execute(stmt)
                session.commit()
                return result.fetchone()
            except Exception as e:
                session.rollback()
                print(e)
                return None
