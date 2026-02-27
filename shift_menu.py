from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDButtonText, MDButton, MDIconButton
from kivymd.uix.dialog import MDDialogContentContainer, MDDialogHeadlineText, MDDialogButtonContainer, MDDialog, \
    MDDialogSupportingText
from kivymd.uix.divider import MDDivider
from kivymd.uix.label import MDLabel
from kivymd.uix.list import MDList, MDListItemTertiaryText, MDListItemSupportingText, MDListItemHeadlineText, MDListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.widget import MDWidget

from common import snack_bar
from headers import TOP_APP_BAR_COLOR, Shift, Barista
from order_menu import OrderMenu


class ShiftMenu:
    def __init__(self):
        self.order_menu = OrderMenu()

    def show_shift_order_history(self, shift):
        shift.get_orders()
        self.order_menu.show_order_history(shift)

    def shift_list_update(self, shifts_list=None):
        self.shift_list.clear_widgets()

        app = MDApp.get_running_app()
        shifts = shifts_list or app.shift.get_all_shifts(app.shift.barista)

        for shift in reversed(shifts):
            time_text = f"{shift.start_time.strftime('%H:%M')} - {shift.end_time.strftime('%H:%M') if shift.end_time else 'Не закрыта'}"

            shift_list_item = MDListItem(
                MDListItemHeadlineText(
                    text=f"Смена {shift.start_time.strftime('%d.%m.%Y')}",
                    theme_text_color="Custom",
                    text_color="black",
                    font_style="Title",
                    role="medium",
                    bold=False
                ),
                MDListItemSupportingText(
                    text=time_text,
                    theme_text_color="Custom",
                    text_color="black",
                    font_style="Title",
                    role="small",
                    bold=False
                ),
                MDListItemTertiaryText(
                    text=f"{shift.order_amount} "
                         f"{'заказов' if shift.order_amount > 4 else 'заказа' if shift.order_amount > 1 else 'заказ'} "
                         f"на сумму {shift.revenue:.2f} BYN",
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
                    on_release=lambda x, s=shift, b=app.shift.barista: self.show_shift_menu(x, s, b)
                ),
                divider=True,
                divider_color="black",
                theme_bg_color="Custom",
                md_bg_color=TOP_APP_BAR_COLOR,
                on_release=lambda x, s=shift: self.show_shift_order_history(s)
            )
            self.shift_list.add_widget(shift_list_item)

    def shift_list_total_value_update(self, shifts_list=None):
        self.shift_total_value.clear_widgets()

        app = MDApp.get_running_app()
        shifts = shifts_list or app.shift.get_all_shifts(app.shift.barista)

        total_label = MDLabel(
            text="Всего:",
            theme_text_color="Custom",
            text_color="black",
            size_hint_x=0.3
        )

        total_amount = len(shifts)
        total_hours = sum(shift.total_hours for shift in shifts if shift.total_hours)

        shifts_text = f"{total_amount} {'смен' if total_amount > 4 else 'смены' if total_amount > 1 else 'смена'}"
        cart_total_amount_label = MDLabel(
            text=shifts_text,
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            adaptive_width=True
        )

        cart_total_value_label = MDLabel(
            text=f"{total_hours} часов",
            theme_text_color="Custom",
            text_color="black",
            bold=True,
            halign="right",
        )

        self.shift_total_value.add_widget(total_label)
        self.shift_total_value.add_widget(cart_total_amount_label)
        self.shift_total_value.add_widget(cart_total_value_label)

    def show_shifts(self):
        app = MDApp.get_running_app()
        shifts = app.shift.get_all_shifts(app.shift.barista)

        if not shifts:
            snack_bar("История смен пуста!")
            return

        header_box = MDBoxLayout(
            orientation="horizontal",
            adaptive_height=True,
            spacing=5,
            padding=[5, 5, 5, 5],
        )

        shift_date_label = MDLabel(
            text="Смены",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=25
        )

        barista_label = MDLabel(
            text=f"Бариста {app.shift.barista.name}",
            halign="right",
            theme_text_color="Custom",
            text_color="black",
            size_hint_y=None,
            height=25
        )

        header_box.add_widget(shift_date_label)
        header_box.add_widget(barista_label)

        self.shift_list = MDList()
        self.shift_list_update(shifts)

        shift_list_scroll_view = MDScrollView(
            size_hint_y=None,
            height=300
        )
        shift_list_scroll_view.add_widget(self.shift_list)

        self.shift_total_value = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=50,
            spacing=5,
            padding=5,
        )
        self.shift_list_total_value_update(shifts)

        shifts_history_dialog = MDDialog(
            MDDialogHeadlineText(text="История смен", theme_text_color="Custom", text_color="black"),
            MDDialogContentContainer(
                header_box,
                MDDivider(),
                shift_list_scroll_view,
                MDDivider(),
                self.shift_total_value,
                orientation="vertical",
            ),
            MDDialogButtonContainer(
                MDWidget(),
                MDButton(
                    MDButtonText(text="Закрыть", theme_text_color="Custom", text_color="black"),
                    style="text",
                    on_release=lambda x: shifts_history_dialog.dismiss()
                ),
            ),
            size_hint=(0.9, None),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        shifts_history_dialog.open()

    def shift_delete(self, shift: Shift, barista: Barista):
        self.shift_menu.dismiss()

        dialog = MDDialog(
            MDDialogHeadlineText(
                text="Удалить смену?",
                theme_text_color="Custom",
                text_color="black"),
            MDDialogSupportingText(
                text=f"Удалить смену {shift.start_time.strftime('%d.%m.%Y')}?",
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
                    on_release=lambda x: self.confirm_shift_delete(shift, dialog, barista)
                ),
            ),
            theme_bg_color="Custom",
            md_bg_color="white",
            radius=[5, 5, 5, 5],
        )
        dialog.open()

    def confirm_shift_delete(self, shift: Shift, dialog, barista: Barista):
        app = MDApp.get_running_app()
        app.shift.delete(shift)

        dialog.dismiss()

    def show_shift_menu(self, button, shift, barista):
        menu_items = [
            {
                "text": "Удалить",
                "leading_icon": "trash-can-outline",
                "on_release": lambda x=None, o=shift, b=barista: self.shift_delete(o, b),
            },
        ]

        self.shift_menu = MDDropdownMenu(
            items=menu_items,
            width=200,
            position="auto",
            caller=button,
        )

        self.shift_menu.open()
