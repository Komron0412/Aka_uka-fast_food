from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

import methods
from db_instance import db
import globals
import admin


async def inline_handler(update, context):
    query = update.callback_query
    await query.answer()
    data_sp = str(query.data).split("_")
    db_user = db.get_user_by_chat_id(query.message.chat_id)
    lang_code = globals.LANGUAGE_CODE[db_user['lang_id']]

    # Initialize product_quantities if not exists
    if "product_quantities" not in context.user_data:
        context.user_data["product_quantities"] = {}

    # Handle increase quantity
    if data_sp[0] == "increase":
        product_id = data_sp[1]

        # Get current quantity or default to 1
        current_qty = context.user_data["product_quantities"].get(product_id, 1)

        # Increment quantity
        new_qty = current_qty + 1
        context.user_data["product_quantities"][product_id] = new_qty

        # Get product info
        product = db.get_product_by_id(int(product_id))

        # Create updated buttons
        buttons = [
            [
                InlineKeyboardButton(
                    text="➖",
                    callback_data=f"decrease_{product_id}"
                ),
                InlineKeyboardButton(
                    text=str(new_qty),
                    callback_data=f"quantity_{product_id}"
                ),
                InlineKeyboardButton(
                    text="➕",
                    callback_data=f"increase_{product_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"🛒 {globals.BTN_ADD_TO_CART[db_user['lang_id']]}",
                    callback_data=f"add_to_cart_{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"⬅️ {globals.BTN_BACK[db_user['lang_id']]}",
                    callback_data=f"category_product_back_{product['category_id']}"
                )
            ]
        ]

        # Update caption
        caption = f"{globals.TEXT_PRODUCT_PRICE[db_user['lang_id']]} {product['price']}\n"
        caption += f"{globals.TEXT_PRODUCT_DESC[db_user['lang_id']]} {product[f'description_{lang_code}']}\n"
        caption += f"\n{globals.TEXT_QUANTITY[db_user['lang_id']]}: {new_qty}"

        await query.edit_message_caption(
            caption=caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        return

    # Handle decrease quantity
    elif data_sp[0] == "decrease":
        product_id = data_sp[1]

        # Get current quantity or default to 1
        current_qty = context.user_data["product_quantities"].get(product_id, 1)

        # Decrement quantity but don't go below 1
        new_qty = max(1, current_qty - 1)
        context.user_data["product_quantities"][product_id] = new_qty

        # Get product info
        product = db.get_product_by_id(int(product_id))

        # Create updated buttons
        buttons = [
            [
                InlineKeyboardButton(
                    text="➖",
                    callback_data=f"decrease_{product_id}"
                ),
                InlineKeyboardButton(
                    text=str(new_qty),
                    callback_data=f"quantity_{product_id}"
                ),
                InlineKeyboardButton(
                    text="➕",
                    callback_data=f"increase_{product_id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"🛒 {globals.BTN_ADD_TO_CART[db_user['lang_id']]}",
                    callback_data=f"add_to_cart_{product_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"⬅️ {globals.BTN_BACK[db_user['lang_id']]}",
                    callback_data=f"category_product_back_{product['category_id']}"
                )
            ]
        ]

        # Update caption
        caption = f"{globals.TEXT_PRODUCT_PRICE[db_user['lang_id']]} {product['price']}\n"
        caption += f"{globals.TEXT_PRODUCT_DESC[db_user['lang_id']]} {product[f'description_{lang_code}']}\n"
        caption += f"\n{globals.TEXT_QUANTITY[db_user['lang_id']]}: {new_qty}"

        await query.edit_message_caption(
            caption=caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        return

    # Handle add to cart
    elif data_sp[0] == "add" and data_sp[1] == "to" and data_sp[2] == "cart":
        product_id = data_sp[3]

        # Get quantity (default to 1 if not set)
        quantity = context.user_data["product_quantities"].get(product_id, 1)

        # Initialize cart if it doesn't exist
        if "carts" not in context.user_data:
            context.user_data["carts"] = {}

        # Add to cart or update quantity
        if product_id in context.user_data["carts"]:
            context.user_data["carts"][product_id] += quantity
        else:
            context.user_data["carts"][product_id] = quantity

        # Reset the product quantity after adding to cart
        context.user_data["product_quantities"][product_id] = 1

        # Delete current message and show cart
        await query.message.delete()

        # Show updated cart
        carts = context.user_data.get("carts", {})
        categories = db.get_categories_by_parent()
        buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])

        text = f"{globals.AT_STORE[db_user['lang_id']]}:\n\n"
        total_price = 0
        for cart, val in carts.items():
            product = db.get_products_for_cart(int(cart))
            text += f"{val} x {product[f'cat_name_{lang_code}']} {product[f'name_{lang_code}']}\n"
            total_price += product['price'] * val

        text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price}"
        buttons.append([InlineKeyboardButton(text=f"{globals.BTN_KORZINKA[db_user['lang_id']]}", callback_data="cart")])

        await query.message.reply_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=buttons,
            )
        )
        return

    # Original category logic
    if data_sp[0] == "category":
        if data_sp[1] == "product":
            if data_sp[2] == "back":
                await query.message.delete()
                products = db.get_products_by_category(category_id=int(data_sp[3]))
                buttons = methods.send_product_buttons(products=products, lang_id=db_user["lang_id"])

                clicked_btn = db.get_category_parent(int(data_sp[3]))

                if clicked_btn and clicked_btn['parent_id']:
                    buttons.append([InlineKeyboardButton(
                        text="Back", callback_data=f"category_back_{clicked_btn['parent_id']}"
                    )])
                else:
                    buttons.append([InlineKeyboardButton(
                        text="Back", callback_data=f"category_back"
                    )])

                await query.message.reply_text(
                    text=globals.TEXT_ORDER[db_user['lang_id']],
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=buttons,
                    )
                )

            else:
                product = db.get_product_by_id(int(data_sp[2]))
                await query.message.delete()

                # Initialize quantity for this product
                product_id = str(data_sp[2])
                context.user_data["product_quantities"][product_id] = 1

                caption = f"{globals.TEXT_PRODUCT_PRICE[db_user['lang_id']]} " + str(product["price"]) + \
                          f"\n{globals.TEXT_PRODUCT_DESC[db_user['lang_id']]} " + \
                          product[f"description_{lang_code}"]

                buttons = [
                    [
                        InlineKeyboardButton(
                            text="➖",
                            callback_data=f"decrease_{data_sp[2]}"
                        ),
                        InlineKeyboardButton(
                            text="1",
                            callback_data=f"quantity_{data_sp[2]}"
                        ),
                        InlineKeyboardButton(
                            text="➕",
                            callback_data=f"increase_{data_sp[2]}"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=f"🛒 {globals.BTN_ADD_TO_CART[db_user['lang_id']]}",
                            callback_data=f"add_to_cart_{data_sp[2]}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text=f"⬅️ {globals.BTN_BACK[db_user['lang_id']]}",
                            callback_data=f"category_product_back_{product['category_id']}"
                        )
                    ]
                ]

                await query.message.reply_photo(
                    photo=open(product['image'], "rb"),
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                )

        elif data_sp[1] == "back":
            if len(data_sp) == 3:
                parent_id = int(data_sp[2])
            else:
                print("No parent")
                parent_id = None

            categories = db.get_categories_by_parent(parent_id=parent_id)
            buttons = []
            row = []
            for i in range(len(categories)):
                row.append(
                    InlineKeyboardButton(
                        text=categories[i][f'name_{lang_code}'],
                        callback_data=f"category_{categories[i]['id']}"
                    )
                )

                if len(row) == 2 or (len(categories) % 2 == 1 and i == len(categories) - 1):
                    buttons.append(row)
                    row = []

            if parent_id:
                clicked_btn = db.get_category_parent(parent_id)

                if clicked_btn and clicked_btn['parent_id']:
                    buttons.append([InlineKeyboardButton(
                        text="Back", callback_data=f"category_back_{clicked_btn['parent_id']}"
                    )])
                else:
                    buttons.append([InlineKeyboardButton(
                        text="Back", callback_data=f"category_back"
                    )])

            await query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )
        else:
            categories = db.get_categories_by_parent(parent_id=int(data_sp[1]))
            if categories:
                buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])
            else:
                products = db.get_products_by_category(category_id=int(data_sp[1]))
                buttons = methods.send_product_buttons(products=products, lang_id=db_user["lang_id"])
            clicked_btn = db.get_category_parent(int(data_sp[1]))

            if clicked_btn and clicked_btn['parent_id']:
                buttons.append([InlineKeyboardButton(
                    text="Back", callback_data=f"category_back_{clicked_btn['parent_id']}"
                )])
            else:
                buttons.append([InlineKeyboardButton(
                    text="Back", callback_data=f"category_back"
                )])

            await query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )

    elif data_sp[0] == "cart":
        if len(data_sp) == 2 and data_sp[1] == "clear":
            context.user_data.pop("carts")
            categories = db.get_categories_by_parent()
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])
            text = globals.TEXT_ORDER[db_user["lang_id"]]

            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )

        elif len(data_sp) == 2 and data_sp[1] == "back":
            categories = db.get_categories_by_parent()
            buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"])

            if context.user_data.get("carts", {}):
                carts = context.user_data.get("carts")
                text = f"{globals.AT_STORE[db_user['lang_id']]}:\n\n"
                total_price = 0
                for cart, val in carts.items():
                    product = db.get_products_for_cart(int(cart))
                    text += f"{val} x {product[f'cat_name_{lang_code}']} {product[f'name_{lang_code}']}\n"
                    total_price += product['price'] * val

                text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price}"

                buttons.append(
                    [InlineKeyboardButton(text=f"{globals.BTN_KORZINKA[db_user['lang_id']]}", callback_data="cart")])

        else:
            buttons = [
                [
                    InlineKeyboardButton(
                        text=globals.BTN_CHECKOUT[db_user['lang_id']],callback_data="order"
                    ),
                    InlineKeyboardButton(
                        text=globals.BTN_CLEAR_CART[db_user['lang_id']],callback_data="cart_clear"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=globals.BTN_CART_BACK[db_user['lang_id']],callback_data="cart_back"
                    )
                ],
            ]
            await query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=buttons
                )
            )



    elif data_sp[0] == "order":

        # Check if there are additional parameters

        if len(data_sp) == 1:

            # Just "order" - show payment options

            await query.message.edit_reply_markup(

                reply_markup=InlineKeyboardMarkup(

                    [[

                        InlineKeyboardButton(

                            text=globals.BTN_PAYMENT_CASH[db_user['lang_id']],

                            callback_data="order_payment_1"

                        ),

                        InlineKeyboardButton(

                            text=globals.BTN_PAYMENT_CARD[db_user['lang_id']],

                            callback_data="order_payment_2"

                        ),

                    ]]

                )

            )


        elif len(data_sp) > 1 and data_sp[1] == "location":

            # Show order location on map

            order_id = int(data_sp[2])

            order = db.get_order_by_id(order_id)

            if order and order.get('latitude') and order.get('longitude'):

                await query.message.reply_location(

                    latitude=order['latitude'],

                    longitude=order['longitude']

                )

                await query.answer(

                    text="📍 Lokatsiya yuborildi" if db_user['lang_id'] == 1 else "📍 Местоположение отправлено"

                )

            else:

                await query.answer(

                    text="❌ Lokatsiya topilmadi" if db_user['lang_id'] == 1 else "❌ Местоположение не найдено",

                    show_alert=True

                )


        elif len(data_sp) > 1 and data_sp[1] == "cancel":

            # Cancel order

            order_id = int(data_sp[2])

            # Update order status to 0 (cancelled)

            db.update_order_status(order_id, 0)

            await query.answer(

                text="✅ Buyurtma bekor qilindi" if db_user['lang_id'] == 1 else "✅ Заказ отменен",

                show_alert=True

            )

            # Update the message to show cancelled status

            await query.edit_message_text(

                text=query.message.text + "\n\n❌ " + (

                    "Bekor qilindi" if db_user['lang_id'] == 1 else "Отменен"

                )

            )


        elif len(data_sp) > 1 and data_sp[1] == "payment":

            # Payment method selected

            context.user_data['payment_type'] = int(data_sp[2])

            await query.message.delete()

            await query.message.reply_text(

                text=globals.SEND_LOCATION[db_user["lang_id"]],

                reply_markup=ReplyKeyboardMarkup(

                    [[KeyboardButton(text=globals.BTN_SEND_LOCATION[db_user["lang_id"]], request_location=True)]],
                    resize_keyboard=True)
            )
        else:
            await query.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(
                            text=globals.BTN_PAYMENT_CASH[db_user['lang_id']],
                            callback_data="order_payment_1"
                        ),
                        InlineKeyboardButton(
                            text=globals.BTN_PAYMENT_CARD[db_user['lang_id']],
                            callback_data="order_payment_2"
                        ),
                    ]]
                )

            )