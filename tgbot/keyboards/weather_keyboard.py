from aiogram.utils.keyboard import InlineKeyboardBuilder


def select_day_kb():
    # First, you should create an InlineKeyboardBuilder object
    keyboard = InlineKeyboardBuilder()

    # You can use keyboard.button() method to add buttons, then enter text and callback_data
    keyboard.button(
        text="☀️ Сегодня",
        callback_data="today"
    )
    keyboard.button(
        text="📆 Завтра",
        # In this simple example, we use a string as callback_data
        callback_data="tomorrow"
    )

    # If needed you can use keyboard.adjust() method to change the number of buttons per row
    # keyboard.adjust(2)

    # Then you should always call keyboard.as_markup() method to get a valid InlineKeyboardMarkup object
    return keyboard.as_markup()
