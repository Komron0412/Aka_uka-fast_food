# ============================================
# 🌐 WELCOME & LANGUAGE SELECTION
# ============================================

WELCOME_TEXT = """
🎉 Xush kelibsiz AKA_UKA botiga!
🎉 Добро пожаловать в бот AKA_UKA!

Eng mazali fast_foodlar buyurtma qiling! 🍔🍕
Заказывайте самые вкусные блюда! 🍔🍕
"""

CHOOSE_LANG = """
🌍 Tilni tanlang / Выберите язык:
"""

BTN_LANG_UZ = "🇺🇿 O'zbek tili"
BTN_LANG_RU = "🇷🇺 Русский язык"

# ============================================
# 🔐 STATES
# ============================================

STATES = {
    "reg": 1,
    "menu": 2,
    "settings": 3
}

LANGUAGE_CODE = {
    1: "uz",
    2: "ru"
}

# ============================================
# ⚠️ WARNINGS & ERRORS
# ============================================

TEXT_LANG_WARNING = """
⚠️ Iltimos, tillardan birini tanlang!
⚠️ Пожалуйста, выберите один из языков!
"""

# ============================================
# 📝 REGISTRATION TEXTS
# ============================================

TEXT_ENTER_FIRST_NAME = {
    1: "👤 Iltimos, ismingizni kiriting:",
    2: "👤 Пожалуйста, введите ваше имя:"
}

TEXT_ENTER_LAST_NAME = {
    1: "👤 Iltimos, familiyangizni kiriting:",
    2: "👤 Пожалуйста, введите вашу фамилию:"
}

BTN_SEND_CONTACT = {
    1: "📱 Telefon raqamni yuborish",
    2: "📱 Отправить номер телефона"
}

TEXT_ENTER_CONTACT = {
    1: """
📞 Iltimos, telefon raqamingizni yuboring!

Pastdagi tugmani bosing yoki raqamni kiriting:
    """,
    2: """
📞 Пожалуйста, отправьте свой номер телефона!

Нажмите кнопку ниже или введите номер:
    """
}

# ============================================
# 🏠 MAIN MENU
# ============================================

TEXT_MAIN_MENU = {
    1: "🏠 Asosiy menyu",
    2: "🏠 Главное меню"
}

BTN_ORDER = {
    1: "🛒 Buyurtma berish",
    2: "🛒 Сделать заказ"
}

TEXT_ORDER = {
    1: "📋 Kategoriyani tanlang va buyurtma bering!",
    2: "📋 Выберите категорию и сделайте заказ!"
}

BTN_MY_ORDERS = {
    1: "📦 Mening buyurtmalarim",
    2: "📦 Мои заказы"
}

BTN_EVOS_FAMILY = {
    1: "👨‍👩‍👧‍👦 AKA_UKA Oilasi",
    2: "👨‍👩‍👧‍👦 Семья AKA_UKA"
}

BTN_COMMENTS = {
    1: "⭐️ Fikr bildirish",
    2: "⭐️ Оставить отзыв"
}

BTN_SETTINGS = {
    1: "⚙️ Sozlamalar",
    2: "⚙️ Настройки"
}


# ============================================
# 🛍️ CART & PRODUCTS
# ============================================

BTN_KORZINKA = {
    1: "🛒 Savat",
    2: "🛒 Корзина"
}

BTN_ADD_TO_CART = {
    1: "➕ Savatga qo'shish",
    2: "➕ Добавить в корзину"
}

BTN_BACK = {
    1: "◀️ Ortga",
    2: "◀️ Назад"
}

TEXT_QUANTITY = {
    1: "📊 Miqdor",
    2: "📊 Количество"
}

TEXT_PRODUCT_PRICE = {
    1: "💰 Narxi:",
    2: "💰 Цена:"
}

TEXT_PRODUCT_DESC = {
    1: "📝 Tavsifi:",
    2: "📝 Описание:"
}

AT_STORE = {
    1: "🛒 Savatingizda:",
    2: "🛒 В вашей корзине:"
}

ALL = {
    1: "💵 Jami",
    2: "💵 Итого"
}

ZAKAZ = {
    1: "📦 Buyurtma",
    2: "📦 Заказ"
}

SUM = {
    1: "so'm",
    2: "сум"
}

NO_ZAKAZ = {
    1: """
😔 Sizning savatingiz bo'sh!

Buyurtma berish uchun mahsulotlarni tanlang.
    """,
    2: """
😔 Ваша корзина пуста!

Выберите товары для оформления заказа.
    """
}
# ============================================
# 🔘 CART ACTION BUTTONS
# ============================================

BTN_CHECKOUT = {
    1: "✅ Buyurtma berish",
    2: "✅ Оформить заказ"
}

BTN_CLEAR_CART = {
    1: "🗑 Savatni tozalash",
    2: "🗑 Очистить корзину"
}

BTN_CART_BACK = {
    1: "◀️ Orqaga",
    2: "◀️ Назад"
}

# ============================================
# 📍 LOCATION & PAYMENT
# ============================================

SEND_LOCATION = {
    1: "📍 Manzilingizni yuboring",
    2: "📍 Отправьте ваш адрес"
}

TEXT_LOCATION_INSTRUCTION = {
    1: """
📍 Yetkazib berish manzilini yuboring

Pastdagi tugmani bosing yoki joylashuvingizni yuboring.
    """,
    2: """
📍 Отправьте адрес доставки

Нажмите кнопку ниже или отправьте ваше местоположение.
    """
}

BTN_SEND_LOCATION = {
    1: "📍 Joylashuvni yuborish",
    2: "📍 Отправить местоположение"
}
# ============================================
# 💳 PAYMENT METHOD BUTTONS
# ============================================


TEXT_PAYMENT_METHOD = {
    1: "💳 To'lov turini tanlang:",
    2: "💳 Выберите способ оплаты:"
}

BTN_PAYMENT_CASH = {
    1: "💵 Naqd pul",
    2: "💵 Наличные"
}

BTN_PAYMENT_CARD = {
    1: "💳 Plastik karta",
    2: "💳 Банковская карта"
}

# ============================================
# ✅ SUCCESS MESSAGES
# ============================================

TEXT_MY_ORDERS_TITLE = {
    1: "📦 Mening buyurtmalarim",
    2: "📦 Мои заказы"
}

TEXT_NO_ORDERS = {
    1: """
😔 Sizda hali buyurtmalar yo'q

Buyurtma berish uchun menyudan tanlang! 🍔
    """,
    2: """
😔 У вас пока нет заказов

Выберите из меню, чтобы сделать заказ! 🍔
    """
}

TEXT_ORDER_DETAILS = {
    1: """
📦 Buyurtma #{order_id}

📅 Sana: {date}
💳 To'lov turi: {payment}
📊 Status: {status}
📍 Manzil: {location}

🛒 Mahsulotlar:
{products}

💰 Jami: {total} so'm
    """,
    2: """
📦 Заказ #{order_id}

📅 Дата: {date}
💳 Способ оплаты: {payment}
📊 Статус: {status}
📍 Адрес: {location}

🛒 Товары:
{products}

💰 Итого: {total} сум
    """
}

ORDER_STATUS = {
    1: {
        0: "❌ Bekor qilindi",
        1: "⏳ Kutilmoqda",
        2: "✅ Tasdiqlandi",
        3: "🚚 Yetkazilmoqda",
        4: "✅ Yetkazildi"
    },
    2: {
        0: "❌ Отменен",
        1: "⏳ Ожидание",
        2: "✅ Подтвержден",
        3: "🚚 Доставляется",
        4: "✅ Доставлен"
    }
}

PAYMENT_TYPE = {
    1: {
        1: "💵 Naqd pul",
        2: "💳 Plastik karta"
    },
    2: {
        1: "💵 Наличные",
        2: "💳 Банковская карта"
    }
}

TEXT_ADDED_TO_CART = {
    1: "✅ Savatga qo'shildi!",
    2: "✅ Добавлено в корзину!"
}

TEXT_CART_CLEARED = {
    1: "🗑 Savat tozalandi!",
    2: "🗑 Корзина очищена!"
}

# ============================================
# ℹ️ ABOUT & INFO
# ============================================

ABOUT_COMPANY = {
    1: """
🍔 AKA_UKA haqida

AKA_UKA - Alimkentdagi eng yaxshi fast-food tarmog'i!

✨ Biz taklif qilamiz:
• Yangi va mazali taomlar
• Tez yetkazib berish xizmati
• Qulay narxlar
• Yuqori sifat

📞 Aloqa: +998 909185734
    """,
    2: """
🍔 О AKA_UKA

AKA_UKA - лучшая сеть фастфуда в Alimekent!

✨ Мы предлагаем:
• Свежие и вкусные блюда
• Быструю доставку
• Доступные цены
• Высокое качество

📞 Контакты: +998 909185734
    """
}

# ============================================
# 🔘 CART ACTION BUTTONS
# ============================================


BTN_CONTINUE_SHOPPING = {
    1: "🛍 Xarid davom ettirish",
    2: "🛍 Продолжить покупки"
}

TEXT_ADMIN_PANEL = {
    1: "👨‍💼 Admin panel",
    2: "👨‍💼 Админ панель"
}