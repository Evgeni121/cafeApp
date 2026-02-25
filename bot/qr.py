import datetime
import os

from qrcode.main import QRCode
from qrcode.constants import ERROR_CORRECT_L
from aiogram.utils.deep_linking import create_start_link

from headers import Order


class QR:
    QR_PURCHASE_KEY = "purchase_order_id_"
    QR_FREE_KEY = "free_drink_ids_"

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def generate_qr(link: str):
        filepath = "assets/temp/qr.png"

        if os.path.exists(filepath):
            os.remove(filepath)
            print("remove")

        qr = QRCode(version=1, error_correction=ERROR_CORRECT_L, box_size=8, border=4)
        qr.add_data(link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filepath)

        return filepath

    # ---------------------------------------------------------------------------------
    async def encode_order(self, order: Order):
        code = int(datetime.datetime.now().timestamp())
        link = await create_start_link(self.bot, f'{self.QR_PURCHASE_KEY}{order.order_id}_{code}', encode=True)
        filepath = self.generate_qr(link)

        return filepath

    async def encode_free_order(self, order: Order):
        ids = "_".join([str(item.drink.drink_id) for item in order.items for _ in range(item.quantity)])

        code = int(datetime.datetime.now().timestamp())
        link = await create_start_link(self.bot, f'{self.QR_FREE_KEY}{ids}_{code}', encode=True)
        filepath = self.generate_qr(link)

        return filepath
