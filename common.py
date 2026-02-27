from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText


def snack_bar(text):
    MDSnackbar(
        MDSnackbarText(
            text=text,
            theme_text_color="Custom",
            text_color="black"
        ),
        y=20,
        pos_hint={"center_x": 0.5},
        size_hint_x=0.8,
        theme_bg_color="Primary",
        radius=[10, 10, 10, 10],
        duration=1,
    ).open()
