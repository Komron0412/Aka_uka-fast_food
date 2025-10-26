import logging
from typing import List, Dict
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from database import Database, dict_fetchall, dict_fetchone
import globals
import methods
from config import ADMIN_ID

logger = logging.getLogger(__name__)
db = Database("db-evos.db")


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
        db.cur.execute("""
            SELECT o.*, u.first_name, u.last_name, u.phone_number 
            FROM "order" o 
            JOIN user u ON o.user_id = u.id 
            ORDER BY o.created_at DESC 
            LIMIT ?
        """, (limit,))
        orders = dict_fetchall(db.cur)
        
        if not orders:
            await context.bot.send_message(
                chat_id=chat_id,
                text="📋 Hech qanday buyurtma yo'q"
            )
            return
        
        for order in orders:
            status_text = db.get_order_status_text(order['status'], lang_id)
            
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
        db.cur.execute("""
            SELECT o.*, u.first_name, u.last_name, u.phone_number 
            FROM "order" o 
            JOIN user u ON o.user_id = u.id 
            WHERE o.id = ?
        """, (order_id,))
        order = dict_fetchone(db.cur)
        
        if not order:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Buyurtma topilmadi"
            )
            return
        
        # Get order products
        products = db.get_order_products(order_id)
        
        status_text = db.get_order_status_text(order['status'], lang_id)
        
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
        success = db.update_order_status(order_id, status)
        
        if not success:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text="❌ Buyurtma holatini yangilashda xatolik"
            )
            return
        
        # Get order and user info
        try:
            db.cur.execute("""
                SELECT o.*, u.chat_id, u.lang_id 
                FROM "order" o 
                JOIN user u ON o.user_id = u.id 
                WHERE o.id = ?
            """, (order_id,))
            order = dict_fetchone(db.cur)
        except Exception:
            # Fallback for older database structure
            db.cur.execute("""
                SELECT o.*, u.chat_id, u.lang_id 
                FROM "order" o, user u 
                WHERE o.user_id = u.id AND o.id = ?
            """, (order_id,))
            order = dict_fetchone(db.cur)
        
        if order:
            status_text = db.get_order_status_text(status, order['lang_id'])
            
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
            text=f"✅ Buyurtma #{order_id} holati yangilandi: {db.get_order_status_text(status, lang_id)}"
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
        db.cur.execute("SELECT COUNT(*) as count FROM 'order'")
        total_orders = dict_fetchone(db.cur)['count']
        
        # Today's orders
        db.cur.execute("""
            SELECT COUNT(*) as count FROM "order" 
            WHERE DATE(created_at) = DATE('now')
        """)
        today_orders = dict_fetchone(db.cur)['count']
        
        # Total revenue - check if total_amount column exists
        try:
            db.cur.execute("PRAGMA table_info('order')")
            columns = [column[1] for column in db.cur.fetchall()]
            
            if 'total_amount' in columns:
                db.cur.execute("""
                    SELECT SUM(total_amount) as total FROM "order" 
                    WHERE status = 5
                """)
                result = dict_fetchone(db.cur)
                total_revenue = result['total'] if result['total'] else 0
            else:
                # Calculate from order_products if total_amount doesn't exist
                db.cur.execute("""
                    SELECT SUM(op.quantity * p.price) as total FROM "order" o
                    JOIN order_products op ON o.id = op.order_id
                    JOIN product p ON op.product_id = p.id
                    WHERE o.status = 5
                """)
                result = dict_fetchone(db.cur)
                total_revenue = result['total'] if result['total'] else 0
        except Exception:
            total_revenue = 0
        
        # Active users
        db.cur.execute("""
            SELECT COUNT(DISTINCT user_id) as count FROM "order" 
            WHERE DATE(created_at) >= DATE('now', '-7 days')
        """)
        active_users = dict_fetchone(db.cur)['count']
        
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
        db.cur.execute("SELECT chat_id FROM user WHERE is_blocked = 0")
        users = dict_fetchall(db.cur)
        
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
