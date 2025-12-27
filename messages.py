import methods
from register import check, check_data_decorator
from db_instance import db
import globals
from telegram import KeyboardButton, InlineKeyboardMarkup,InlineKeyboardButton, ReplyKeyboardMarkup




@check_data_decorator
async def message_handler(update, context):
    try:
        message = update.message.text
        user = update.message.from_user
        state = context.user_data.get("state", 0)
        db_user = await db.get_user_by_chat_id(user.id)
        if state == 0:
          await check(update, context)

        elif state == 1:
            if not db_user["lang_id"]:

                if message == globals.BTN_LANG_UZ:
                    await db.update_user_data(user.id, "lang_id", 1)
                    await check(update, context)

                elif message == globals.BTN_LANG_RU:
                    await db.update_user_data(user.id, "lang_id", 2)
                    await check(update, context)

                else:
                    await update.message.reply_text(
                        text=globals.TEXT_LANG_WARNING
                    )

            elif not db_user["first_name"]:
                # Basic name validation
                if len(message) < 2:
                    await update.message.reply_text(
                        text="❌ Ismingiz juda qisqa! Iltimos, qaytadan kiriting:" if db_user['lang_id'] == 1 else "❌ Ваше имя слишком короткое! Пожалуйста, введите заново:"
                    )
                    return

                await db.update_user_data(user.id, "first_name", message)
                await check(update, context)

            elif not db_user["phone_number"]:
                # Phone number validation (basic regex check could be added)
                # But here we handle text input if they didn't use the button
                import re
                phone_pattern = re.compile(r'^\+?998\d{9}$')
                
                # Remove spaces and dashes for checking
                clean_phone = message.replace(" ", "").replace("-", "")
                if not phone_pattern.match(clean_phone) and not message.isdigit():
                     await update.message.reply_text(
                        text="❌ Telefon raqami noto'g'ri! Format: +998901234567" if db_user['lang_id'] == 1 else "❌ Неверный номер телефона! Формат: +998901234567"
                    )
                     return

                await db.update_user_data(user.id, "phone_number", clean_phone)
                await check(update, context)

            else:
                await check(update, context)

        elif state == 2:
            if message == globals.BTN_ORDER[db_user['lang_id']]:
                categories = await db.get_categories_by_parent()
                has_cart = bool(context.user_data.get("carts"))
                buttons = methods.send_category_buttons(categories=categories, lang_id=db_user["lang_id"], has_cart=has_cart)
                await update.message.reply_text(
                    text=globals.TEXT_ORDER[db_user['lang_id']],
                    reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=buttons,
                    )
                )
            elif message == globals.BTN_MY_ORDERS[db_user['lang_id']]:
                orders = await db.get_user_orders(db_user['id'])

                if not orders:
                    # No orders found
                    await update.message.reply_text(
                        text=globals.TEXT_NO_ORDERS[db_user['lang_id']]
                    )
                else:
                    # Display each order
                    lang_id = db_user['lang_id']
                    lang_code = globals.LANGUAGE_CODE[lang_id]

                    for order in orders:
                        # Get order products
                        order_products = await db.get_order_products(order['id'])

                        # Format products list
                        products_text = ""
                        total_price = 0

                        for item in order_products:
                            product_name = item[f'product_name_{lang_code}']
                            product_price = item['product_price']
                            amount = item['amount']
                            item_total = product_price * amount

                            products_text += f"  • {amount} x {product_name} - {item_total:,} {globals.SUM[lang_id]}\n"
                            total_price += item_total

                        # Format date
                        order_date = order['created_at'].split('.')[0] if '.' in order['created_at'] else order[
                            'created_at']

                        # Get payment type
                        payment_type_id = int(order.get('payment_type', 1))
                        payment_text = globals.PAYMENT_TYPE[lang_id].get(payment_type_id, "N/A")

                        # Get status
                        status = order.get('status', 1)
                        status_text = globals.ORDER_STATUS[lang_id].get(status, "N/A")

                        # Get location
                        if order.get('latitude') and order.get('longitude'):
                            location_text = f"{order['latitude']}, {order['longitude']}"
                        else:
                            location_text = "N/A"

                        # Format order details
                        order_text = globals.TEXT_ORDER_DETAILS[lang_id].format(
                            order_id=order['id'],
                            date=order_date,
                            payment=payment_text,
                            status=status_text,
                            location=location_text,
                            products=products_text,
                            total=f"{total_price:,}"
                        )

                        # Create buttons for order actions
                        buttons = [
                            [
                                InlineKeyboardButton(
                                    text="📍 Xaritada ko'rish" if lang_id == 1 else "📍 Показать на карте",
                                    callback_data=f"order_location_{order['id']}"
                                )
                            ],
                            [
                                InlineKeyboardButton(
                                    text="❌ Bekor qilish" if lang_id == 1 else "❌ Отменить",
                                    callback_data=f"order_cancel_{order['id']}"
                                )
                            ]
                        ]

                        await update.message.reply_text(
                            text=order_text,
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                        )

            elif message == globals.BTN_EVOS_FAMILY[db_user['lang_id']]:
                await update.message.reply_text(
                    text=globals.ABOUT_COMPANY[db_user['lang_id']]
                )


            elif message == globals.BTN_SETTINGS[db_user['lang_id']]:
                buttons = [
                    [KeyboardButton(text=globals.BTN_LANG_UZ), KeyboardButton(text=globals.BTN_LANG_RU)]
                ]
                await update.message.reply_text(
                    text=globals.CHOOSE_LANG,
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=buttons,
                        resize_keyboard=True,
                    )
                )
                context.user_data["state"] = globals.STATES["settings"]

            elif message == globals.BTN_CART_BACK[db_user['lang_id']]:
                # Back to payment choice from location request
                buttons = [
                    [
                        InlineKeyboardButton(
                            text=globals.BTN_PAYMENT_CASH[db_user['lang_id']],
                            callback_data="order_payment_1"
                        ),
                        InlineKeyboardButton(
                            text=globals.BTN_PAYMENT_CARD[db_user['lang_id']],
                            callback_data="order_payment_2"
                        ),
                    ],
                    [
                        InlineKeyboardButton(
                            text=globals.BTN_BACK[db_user['lang_id']],
                            callback_data="cart"
                        )
                    ]
                ]
                await update.message.reply_text(
                    text=globals.TEXT_PAYMENT_METHOD[db_user['lang_id']],
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
                )

        elif state == 3:
            if message == globals.BTN_LANG_UZ:
                await db.update_user_data(db_user['chat_id'],'lang_id',1)
                context.user_data["state"] = globals.STATES["reg"]
                await check(update, context)

            elif message == globals.BTN_LANG_RU:
                await db.update_user_data(db_user['chat_id'], 'lang_id', 2)
                context.user_data["state"] = globals.STATES["reg"]
                await check(update, context)

            else:
                await update.message.reply_text(
                    text=globals.TEXT_LANG_WARNING
                )


        else:
            await update.message.reply_text("Salom")
    except Exception as e:
        import logging
        logging.error(f"Error in message_handler: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Iltimos, /start buyrug'ini bosing." if (not db_user or db_user.get('lang_id', 1) == 1) else "❌ Произошла ошибка. Пожалуйста, нажмите /start.")
