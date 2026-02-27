import asyncio
import os

from kivy.uix.image import Image
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.dialog import MDDialog, MDDialogContentContainer, MDDialogHeadlineText, MDDialogButtonContainer, \
    MDDialogSupportingText
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, MDListItemTertiaryText, MDListItemSupportingText, MDListItemHeadlineText, MDListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.widget import MDWidget

from common import snack_bar
from headers import Order, TOP_APP_BAR_COLOR, Shift


class OrderMenu:
    def __init__(self):
        pass

    def order_list_update(self, shift):
        self.order_list.clear_widgets()

        for order in reversed(shift.orders):
            order_list_item = MDListItem(
                MDListItemHeadlineText(
                    text=f"Заказ №{order.order_id}",
                    theme_text_color="Custom",
                    text_color="black",
                    font_style="Title",
                    role="medium",
                    bold=False
                ),
                MDListItemSupportingText(
                    text=order.created_at,
                    theme_text_color="Custom",
                    text_color="black",
                    font_style="Title",
                    role="small",
                    bold=False
                ),
                MDListItemTertiaryText(
                    text=f"{order.drink_amount}"
                         f" {'позиций' if order.drink_amount > 4 else 'позиции' if order.drink_amount > 1 else 'позиция'}"
                         f" на сумму {order.discount_price:.2f} {'PIG' if order.is_free else 'BYN'} {f'(-{order.discount}%)' if order.discount else ''}",
                    theme_text_color="Custom",
                    text_color="black",
                    font_style="Title",
                    role="small",
                    bold=False
                ),
                MDIconButton(
                    icon="dots-vertical",
                    theme_icon_color="Custom",
                    icon_color="black",
                    theme_bg_color="Custom",
                    md_bg_color="white",
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    on_release=lambda x, s=shift, o=order: self.show_order_menu(x, s, o)
                ),
                divider=True,
                divider_color="black",
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                on_release=lambda x, o=order: self.show_order_details(o)
            )

            self.order_list.add_widget(order_list_item)

    def order_list_total_value_update(self, shift):
        self.order_total_value.clear_widgets()

        total_label = MDLabel(
            text="Всего:",
            theme_text_color="Custom",
            text_color="black",
            size_hint_x=0.3
        )

        total_amount = len(shift.orders)
        cart_total_amount_label = MDLabel(
            text=f"{total_amount} {'заказов' if total_amount > 4 else 'заказа' if total_amount > 1 else 'заказ'}",
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            size_hint_x=0.5
        )

        summ = 0
        points = 0
        for order in shift.orders:
            if order.is_free:
                points += order.total_price
            else:
                summ += order.discount_price

        cart_total_value_label = MDLabel(
            text=f"{summ:.2f} BYN + {points:.2f} PIG",
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            halign="right",
        )

        self.order_total_value.add_widget(total_label)
        self.order_total_value.add_widget(cart_total_amount_label)
        self.order_total_value.add_widget(cart_total_value_label)

    def show_order_history(self, target_shift=None):
        app = MDApp.get_running_app()

        shift = target_shift or app.shift
        shift.get_orders()
        orders = shift.orders

        if not orders:
            snack_bar("История заказов пуста!")
            return

        header_box = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=5,
            padding=[5, 5, 5, 5],
        )

        order_id_label = MDLabel(
            text=f"Смена",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=25
        )

        time_label = MDLabel(
            text=f"{shift.start_time.strftime('%d.%m.%Y')}",
            halign="right",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=25
        )

        header_box.add_widget(order_id_label)
        header_box.add_widget(time_label)

        self.order_list = MDList()

        self.order_list_update(shift)

        order_list_scroll_view = MDScrollView(
            size_hint_y=None,
            height=250
        )

        order_list_scroll_view.add_widget(self.order_list)

        self.order_total_value = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=50,
            spacing=5,
            padding=5,
        )

        self.order_list_total_value_update(shift)

        order_history_dialog = MDDialog(
            MDDialogHeadlineText(text="История заказов", theme_text_color="Custom", text_color="black"),
            MDDialogContentContainer(
                header_box,
                MDDivider(),
                order_list_scroll_view,
                MDDivider(),
                self.order_total_value,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Закрыть", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: order_history_dialog.dismiss()
                ),
            ),
            size_hint=(0.85, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )

        order_history_dialog.open()

    def order_delete(self, shift: Shift, order: Order):
        self.order_menu.dismiss()

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Удалить заказ?",
                theme_text_color="Custom",
                text_color="black"),
            MDDialogSupportingText(
                text=f"Удалить заказ №{order.order_id}?",
                theme_text_color="Custom",
                text_color="black"),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(
                        text="Отмена",
                        theme_text_color="Custom",
                        text_color="black"),
                    style="text",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(
                        text="Удалить",
                        theme_text_color="Custom",
                        text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: self.confirm_delete(shift, order, dialog)
                ),
            ),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def confirm_delete(self, shift: Shift, order: Order, dialog):
        dialog.dismiss()

        shift.delete_order(order)

        self.order_list_update(shift)
        self.order_list_total_value_update(shift)

    def show_free_confirmation(self, order: Order):
        app = MDApp.get_running_app()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            qr_path = loop.run_until_complete(app.telegram_bot.qr.encode_free_order(order))
        finally:
            loop.close()

        if os.path.exists(qr_path):
            qr_image = Image(
                source=qr_path,
                size_hint_y=None,
                height=200,
            )
            qr_image.reload()
        else:
            from kivy.uix.label import Label
            qr_image = Label(
                text="QR-код\nнедоступен",
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=200
            )

        dialog = MDDialog(
            MDDialogHeadlineText(text="Заказ будет оформлен после подтверждения баланса!", theme_text_color="Custom", text_color="black"),
            MDDialogContentContainer(
                qr_image,
                MDDialogSupportingText(text=f"Итого: {order.total_price:.2f} PIG - {order.discount}% = {order.discount_price:.2f} PIG",
                                       theme_text_color="Custom", text_color="black"),
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="OK", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: dialog.dismiss()
                ),
            ),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def show_order_confirmation(self, order: Order):
        app = MDApp.get_running_app()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            qr_path = loop.run_until_complete(app.telegram_bot.qr.encode_order(order))
        finally:
            loop.close()

        if os.path.exists(qr_path):
            qr_image = Image(
                source=qr_path,
                size_hint_y=None,
                height=200,
            )
            qr_image.reload()
        else:
            from kivy.uix.label import Label
            qr_image = Label(
                text="QR-код\nнедоступен",
                color=[0.5, 0.5, 0.5, 1],
                size_hint_y=None,
                height=200
            )

        dialog = MDDialog(
            MDDialogHeadlineText(text="Заказ успешно оформлен!", theme_text_color="Custom", text_color="black"),
            MDDialogContentContainer(
                qr_image,
                MDDialogSupportingText(text=f"Заказ №{order.order_id}\n"
                                            f"Время: {order.created_at}\n\n"
                                            f"Итого: {order.total_price:.2f} BYN - {order.discount}% = {order.discount_price:.2f} BYN",
                                       theme_text_color="Custom", text_color="black"),
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="OK", theme_text_color="Custom", text_color="black"),
                    style="filled",
                    theme_bg_color="Custom",
                    md_bg_color="pink",
                    on_release=lambda x: dialog.dismiss()
                ),
            ),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def order_qr_code(self, order: Order):
        self.order_menu.dismiss()
        if order.cafe_user_id:
            snack_bar("QR-код уже использован!")
        else:
            self.show_order_confirmation(order)

    def show_order_menu(self, button, shift: Shift, order: Order):
        order_menu = [
            {
                "text": "QR",
                "leading_icon": "qrcode",
                "on_release": lambda x=None, o=order: self.order_qr_code(o),
            },
            {
                "text": "Удалить",
                "leading_icon": "trash-can-outline",
                "on_release": lambda x=None, s=shift, o=order: self.order_delete(s, o),
            },
        ]

        self.order_menu = MDDropdownMenu(
            items=order_menu,
            width=200,
            position="auto",
            caller=button,
        )
        self.order_menu.open()

    def show_order_details(self, order):
        # Создаем основной контейнер
        main_container = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            padding=10,
            adaptive_height=True
        )

        # Шапка с номером заказа и временем
        header_box = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=5,
            padding=[5, 5, 5, 5],
        )

        order_id_label = MDLabel(
            text=f"Заказ №{order.order_id}",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=25
        )

        time_label = MDLabel(
            text=f"{order.created_at}",
            halign="right",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=25
        )

        header_box.add_widget(order_id_label)
        header_box.add_widget(time_label)

        # Контейнер для товаров
        items_container = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            adaptive_height=True
        )

        # Список товаров
        for idx, item in enumerate(order.items):
            item_box = MDBoxLayout(
                orientation="horizontal",
                adaptive_height=True,
                spacing=10
            )

            # Название товара
            name_label = MDLabel(
                text=f"{idx + 1} {item.drink.name} {item.drink.size} {item.drink.size_unit} x {item.quantity}",
                theme_text_color="Custom",
                text_color="black",
                size_hint_x=0.5,
                size_hint_y=None,
                height=30
            )

            total_label = MDLabel(
                text=f"{item.total_price:.2f} BYN",
                theme_text_color="Custom",
                text_color="black",
                halign="right",
                size_hint_x=0.2,
                size_hint_y=None,
                height=30
            )

            item_box.add_widget(name_label)
            item_box.add_widget(total_label)

            items_container.add_widget(item_box)

        footer_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=50,
            padding=5,
            spacing=5
        )

        total_title = MDLabel(
            text="Итого:",
            theme_text_color="Custom",
            text_color="black",
            size_hint_x=0.3
        )

        txt = f"{order.drink_amount} {'позиций' if order.drink_amount > 4 else 'позиции' if order.drink_amount > 1 else 'позиция'}"
        total_amount = MDLabel(
            text=txt,
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            size_hint_x=0.4
        )

        txt = f"{order.total_price:.2f} {'PIG' if order.is_free else 'BYN'} - {order.discount}% = {order.discount_price:.2f} {'PIG' if order.is_free else 'BYN'}" \
            if order.discount else f"{order.total_price:.2f} {'PIG' if order.is_free else 'BYN'}"

        total_value = MDLabel(
            text=txt,
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            halign="right",
        )

        footer_box.add_widget(total_title)
        footer_box.add_widget(total_amount)
        footer_box.add_widget(total_value)

        # Собираем все вместе
        # main_container.add_widget(header_box)
        # main_container.add_widget(MDDivider())
        main_container.add_widget(items_container)
        # main_container.add_widget(MDDivider())
        # main_container.add_widget(footer_box)

        scroll_view = MDScrollView(
            size_hint=(1, None),
            height=200
        )
        scroll_view.add_widget(main_container)

        order_details_dialog = MDDialog(
            MDDialogHeadlineText(
                text="Детали заказа",
                theme_text_color="Custom",
                text_color="black"
            ),
            MDDialogContentContainer(
                header_box,
                MDDivider(),
                scroll_view,
                MDDivider(),
                footer_box,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Закрыть", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: order_details_dialog.dismiss()
                ),
            ),
            size_hint=(0.8, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )

        order_details_dialog.open()
