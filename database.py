import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Table, MetaData, Column, Integer, String, select, Boolean
from sqlalchemy.orm import sessionmaker

load_dotenv()
address = os.getenv("DATABASE_ADDRESS")

if not address:
    raise "Get DATABASE_ADDRESS error!"

engine = create_engine(f"{address}/postgres", echo=False)
Session = sessionmaker(engine, expire_on_commit=False)

metadata_obj = MetaData()

cafe_user_table = Table(
    "cafe_user",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("cafe_id", Integer),
    Column("is_barista", Boolean)
)

with Session() as session:
    stmt = (select(cafe_user_table)
            .where(cafe_user_table.c.is_barista == True)
            .where(cafe_user_table.c.cafe_id == 1)
            )

    for row in session.execute(stmt):
        print(row)
