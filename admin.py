import logging
from typing import List, Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from db_instance import db
import globals
from config import ADMIN_ID

logger = logging.getLogger(__name__)


async def admin_check(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id == ADMIN_ID


async def send_admin_menu(context, chat_id, lang_id):
    """Send admin panel menu"""
    if not await admin_check(chat_id):
        await context.bot.send_message(
            chat_id=chat_id,
            text=globals.TEXT_ACCESS_DENIED[lang_id]
        )
        return
    
    buttons = [
        [KeyboardButton(text=globals.BTN_ORDERS_MANAGEMENT[lang_id])],
        [KeyboardButton(text=globals.BTN_STATISTICS[lang_id])],
        [KeyboardButton(text=globals.BTN_SEND_MESSAGE[lang_id])],
        [KeyboardButton(text="⬅️ Orqaga")]
    ]
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=globals.TEXT_ADMIN_MENU[lang_id],
        reply_markup=ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    )


async def get_recent_orders(context, chat_id, lang_id, limit: int = 10):
    """Get and send recent orders"""
    try:
        query = """
            SELECT o.*, u.first_name, u.last_name, u.phone_number 
            FROM "order" o 
            JOIN user u ON o.user_id = u.id 
            ORDER BY o.created_at DESC 
            LIMIT ?
        """
        async with db.conn.execute(query, (limit,)) as cursor:
            orders = [dict(row) for row in await cursor.fetchall()]
        
        if not orders:
            await context.bot.send_message(
                chat_id=chat_id,
                text="📋 Hech qanday buyurtma yo'q"
            )
            return
        
        for order in orders:
            status_text = globals.ORDER_STATUS[lang_id].get(order['status'], "N/A")
            
            text = f"""
📋 Buyurtma #{order['id']}
👤 Mijoz: {order['first_name']} {order['last_name']}
📞 Telefon: {order['phone_number']}
💰 Summa: {order['total_amount']} so'm
📅 Vaqt: {order['created_at']}
📦 Holat: {status_text}
            """.strip()
            
            buttons = [
                [
                    InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"admin_accept_{order['id']}"),
                    InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"admin_cancel_{order['id']}")
                ],
                [
                    InlineKeyboardButton(text="📝 Batafsil", callback_data=f"admin_details_{order['id']}")
                ]
            ]
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )
            
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=globals.TEXT_ERROR[lang_id]
        )


async def get_order_details(context, chat_id, order_id: int, lang_id: int):
    """Get detailed order information"""
    try:
        # Get order info
        query = """
            SELECT o.*, u.first_name, u.last_name, u.phone_number 
            FROM "order" o 
            JOIN user u ON o.user_id = u.id 
            WHERE o.id = ?
        """
        async with db.conn.execute(query, (order_id,)) as cursor:
            row = await cursor.fetchone()
            order = dict(row) if row else None
        
        if not order:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Buyurtma topilmadi"
            )
            return
        
        # Get order products
        products = await db.get_order_products(order_id)
        
        status_text = globals.ORDER_STATUS[lang_id].get(order['status'], "N/A")
        
        text = f"""
📋 Buyurtma #{order['id']}
👤 Mijoz: {order['first_name']} {order['last_name']}
📞 Telefon: {order['phone_number']}
📍 Manzil: {order['address'] or 'Kiritilmagan'}
💰 Summa: {order['total_amount']} so'm
📅 Vaqt: {order['created_at']}
📦 Holat: {status_text}

🛍 Mahsulotlar:
        """.strip()
        
        for product in products:
            lang_code = globals.LANGUAGE_CODE[lang_id]
            text += f"\n• {product['quantity']}x {product[f'product_name_{lang_code}']} - {product['price']} so'm"
        
        buttons = [
            [
                InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"admin_accept_{order_id}"),
                InlineKeyboardButton(text="👨‍🍳 Tayyorlash", callback_data=f"admin_preparing_{order_id}")
            ],
            [
                InlineKeyboardButton(text="🚗 Yetkazish", callback_data=f"admin_delivering_{order_id}"),
                InlineKeyboardButton(text="✅ Yetkazildi", callback_data=f"admin_delivered_{order_id}")
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"admin_cancel_{order_id}")
            ]
        ]
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        
    except Exception as e:
        logger.error(f"Error getting order details: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=globals.TEXT_ERROR[lang_id]
        )


async def update_order_status(context, order_id: int, status: int, lang_id: int):
    """Update order status and notify user"""
    try:
        # Update order status
        await db.update_order_status(order_id, status)
        success = True
        
        if not success:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text="❌ Buyurtma holatini yangilashda xatolik"
            )
            return
        
        # Get order and user info
        try:
            query = """
                SELECT o.*, u.chat_id, u.lang_id 
                FROM "order" o 
                JOIN user u ON o.user_id = u.id 
                WHERE o.id = ?
            """
            async with db.conn.execute(query, (order_id,)) as cursor:
                row = await cursor.fetchone()
                order = dict(row) if row else None
        except Exception:
            # Fallback for older database structure
            query = """
                SELECT o.*, u.chat_id, u.lang_id 
                FROM "order" o, user u 
                WHERE o.user_id = u.id AND o.id = ?
            """
            async with db.conn.execute(query, (order_id,)) as cursor:
                row = await cursor.fetchone()
                order = dict(row) if row else None
        
        if order:
            status_text = globals.ORDER_STATUS[order['lang_id']].get(status, "N/A")
            
            # Send notification to user
            notification_texts = {
                2: "✅ Buyurtmangiz qabul qilindi! Tez orada tayyorlanadi.",
                3: "👨‍🍳 Buyurtmangiz tayyorlanmoqda...",
                4: "🚗 Buyurtmangiz yo'lda! Tez orada yetkaziladi.",
                5: "🎉 Buyurtmangiz yetkazildi!"
            }
            
            notification_text = notification_texts.get(status, f"📦 {status_text}")
            
            await context.bot.send_message(
                chat_id=order['chat_id'],
                text=notification_text
            )
        
        # Confirm to admin
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✅ Buyurtma #{order_id} holati yangilandi: {globals.ORDER_STATUS[lang_id].get(status, 'N/A')}"
        )
        
    except Exception as e:
        logger.error(f"Error updating order status: {e}")
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text="❌ Xatolik yuz berdi"
        )


async def get_statistics(context, chat_id, lang_id):
    """Get and send bot statistics"""
    try:
        # Total orders
        async with db.conn.execute("SELECT COUNT(*) as count FROM 'order'") as cursor:
            row = await cursor.fetchone()
            total_orders = row['count']
        
        # Today's orders
        query = """
            SELECT COUNT(*) as count FROM "order" 
            WHERE DATE(created_at) = DATE('now')
        """
        async with db.conn.execute(query) as cursor:
            row = await cursor.fetchone()
            today_orders = row['count']
        
        # Total revenue - check if total_amount column exists
        try:
            async with db.conn.execute("PRAGMA table_info('order')") as cursor:
                rows = await cursor.fetchall()
                columns = [column['name'] for column in rows]
            
            if 'total_amount' in columns:
                query = """
                    SELECT SUM(total_amount) as total FROM "order" 
                    WHERE status = 5
                """
                async with db.conn.execute(query) as cursor:
                    row = await cursor.fetchone()
                    total_revenue = row['total'] if row['total'] else 0
            else:
                # Calculate from order_products if total_amount doesn't exist
                query = """
                    SELECT SUM(op.amount * p.price) as total FROM "order" o
                    JOIN order_product op ON o.id = op.order_id
                    JOIN product p ON op.product_id = p.id
                    WHERE o.status = 5
                """
                async with db.conn.execute(query) as cursor:
                    row = await cursor.fetchone()
                    total_revenue = row['total'] if row['total'] else 0
        except Exception:
            total_revenue = 0
        
        # Active users
        query = """
            SELECT COUNT(DISTINCT user_id) as count FROM "order" 
            WHERE DATE(created_at) >= DATE('now', '-7 days')
        """
        async with db.conn.execute(query) as cursor:
            row = await cursor.fetchone()
            active_users = row['count']
        
        text = f"""
📊 Bot statistikasi:

📦 Jami buyurtmalar: {total_orders}
📅 Bugungi buyurtmalar: {today_orders}
💰 Jami daromad: {total_revenue:.0f} so'm
👥 Faol foydalanuvchilar (7 kun): {active_users}
        """.strip()
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=text
        )
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=globals.TEXT_ERROR[lang_id]
        )


async def send_broadcast_message(context, chat_id, message_text: str, lang_id: int):
    """Send broadcast message to all users"""
    try:
        async with db.conn.execute("SELECT chat_id FROM user") as cursor:
            users = [dict(row) for row in await cursor.fetchall()]
        
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user['chat_id'],
                    text=message_text
                )
                sent_count += 1
            except Exception:
                failed_count += 1
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"📢 Xabar yuborildi:\n✅ Muvaffaqiyatli: {sent_count}\n❌ Xatolik: {failed_count}"
        )
        
    except Exception as e:
        logger.error(f"Error sending broadcast: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text=globals.TEXT_ERROR[lang_id]
        )
