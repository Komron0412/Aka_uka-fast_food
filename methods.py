from telegram import KeyboardButton, ReplyKeyboardMarkup,InlineKeyboardButton
import globals


async def send_main_menu(context, chat_id, lang_id, message_id=None):
    buttons = [
        [KeyboardButton(text=globals.BTN_ORDER[lang_id])],
        [KeyboardButton(text=globals.BTN_MY_ORDERS[lang_id]), KeyboardButton(text=globals.BTN_EVOS_FAMILY[lang_id])],
        [KeyboardButton(text=globals.BTN_COMMENTS[lang_id]), KeyboardButton(text=globals.BTN_SETTINGS[lang_id])]
    ]
    if message_id:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=globals.TEXT_MAIN_MENU[lang_id],
            reply_markup=ReplyKeyboardMarkup(
                keyboard=buttons,
                resize_keyboard=True
            )
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=globals.TEXT_MAIN_MENU[lang_id],
            reply_markup=ReplyKeyboardMarkup(
                keyboard=buttons,
                resize_keyboard=True
            )
        )


def send_category_buttons(categories, lang_id, has_cart=False):
    buttons = []
    row = []
    lang_code = globals.LANGUAGE_CODE[lang_id]
    
    for i in range(len(categories)):
        row.append(
            InlineKeyboardButton(
                text=categories[i][f'name_{lang_code}'],
                callback_data=f"category_{categories[i]['id']}"
            )
        )
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)
    
    if has_cart:
        buttons.append([InlineKeyboardButton(text=f"{globals.BTN_KORZINKA[lang_id]}", callback_data="cart")])

    back_text = "❌ Bekor qilish" if lang_id == 1 else "❌ Отмена"
    buttons.append([InlineKeyboardButton(text=back_text, callback_data="main_menu")])
    
    return buttons

def send_product_buttons(products, lang_id, has_cart=False):
    buttons = []
    row = []
    lang_code = globals.LANGUAGE_CODE[lang_id]
    for i in range(len(products)):
        row.append(
            InlineKeyboardButton(
                text=products[i][f'name_{lang_code}'],
                callback_data=f"category_product_{products[i]['id']}"
            )
        )

        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)
    
    if has_cart:
        buttons.append([InlineKeyboardButton(text=f"{globals.BTN_KORZINKA[lang_id]}", callback_data="cart")])

    back_text = "❌ Bekor qilish" if lang_id == 1 else "❌ Отмена"
    buttons.append([InlineKeyboardButton(text=back_text, callback_data="main_menu")])

    return buttons