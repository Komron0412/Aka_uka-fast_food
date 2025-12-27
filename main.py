import asyncio
from telegram.ext import (CommandHandler, CallbackQueryHandler, MessageHandler, filters,
                          ApplicationBuilder)

from config import ADMIN_ID
from db_instance import db
from register import check
from messages import message_handler
from inlines import inline_handler
from telegram import ReplyKeyboardRemove
from config import TOKEN
import globals
import methods
async def start_handler(update, context):
    if "carts" in context.user_data:
        context.user_data.pop("carts")
    await check(update, context)


async def contact_handler(update, context):
    message = update.message.contact.phone_number
    user = update.message.from_user
    await db.update_user_data(user.id, "phone_number",message)
    await check(update,context)

async def location_handler(update, context):
    db_user = await db.get_user_by_chat_id(update.message.chat_id)
    location = update.message.location
    payment_type = context.user_data.get("payment_type",None)
    await db.create_order(db_user['id'],context.user_data.get("carts",{}),payment_type,location)
    text = ""

    if context.user_data.get("carts", {}):
        carts = context.user_data.get("carts")
        text = "\n"
        lang_code = globals.LANGUAGE_CODE[db_user["lang_id"]]
        total_price = 0
        for cart, val in carts.items():
            product = await db.get_products_for_cart(int(cart))
            text += f"{val} x {product[f'cat_name_{lang_code}']} {product[f'name_{lang_code}']}\n"
            total_price += product['price'] * val

        text += f"\n{globals.ALL[db_user['lang_id']]}: {total_price} {globals.SUM[db_user['lang_id']]}"

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"YANGI BUYURTMA\n\n"
            f"Ism: {db_user['first_name']}\n"
            f"Telfoni:  {db_user['phone_number']}\n"
            f"Buyurtma >>>\n"
            f"{text}",
            reply_markup=ReplyKeyboardRemove()
    )

    # Confirmation to user
    await update.message.reply_text(
        text=globals.TEXT_ORDER_ACCEPTED[db_user['lang_id']],
    )

    # Clear cart and return to menu
    if "carts" in context.user_data:
        context.user_data.pop("carts")
    
    await methods.send_main_menu(context, update.message.chat_id, db_user['lang_id'])



async def main():
    await db.connect()
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_handler))
    app.add_handler(MessageHandler(filters.TEXT, message_handler))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
    app.add_handler(CallbackQueryHandler(inline_handler))
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))

    print("Bot started!!")

    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        # Keep the application running until interrupted
        import asyncio
        while True:
            await asyncio.sleep(1)
    finally:
        await db.close()
        if app.updater.running:
            await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
