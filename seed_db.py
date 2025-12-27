import asyncio
from db_instance import db

async def seed():
    await db.connect()
    
    # Clean tables
    await db.conn.execute("DELETE FROM order_product")
    await db.conn.execute("DELETE FROM \"order\"")
    await db.conn.execute("DELETE FROM product")
    await db.conn.execute("DELETE FROM category")
    await db.conn.commit()

    # Add some categories
    categories = [
        ("🌭 Hot-doglar", "🌭 Хот-доги"),
        ("🍢 Kaboblar", "🍢 Шашлыки"),
        ("☕️ Ichimliklar", "☕️ Напитки"),
    ]
    
    for uz, ru in categories:
        await db.conn.execute("INSERT INTO category (name_uz, name_ru) VALUES (?, ?)", (uz, ru))
    
    await db.conn.commit()
    
    # Get category IDs
    async with db.conn.execute("SELECT id, name_uz FROM category") as cursor:
        rows = await cursor.fetchall()
        cat_ids = {row['name_uz']: row['id'] for row in rows}
    
    # Add some products
    products = [
        ("Qiymali xot-dog", "Хот-дог с фаршем", cat_ids["🌭 Hot-doglar"], 15000, "Mazali qiymali xot-dog", "Вкусный хот-дог с фаршем", "images/Qiymali_xot.png"),
        ("Maxsus xot-dog", "Специальный хот-дог", cat_ids["🌭 Hot-doglar"], 20000, "Maxsus ingrediyentlar bilan", "Со специальными ингредиентами", "images/Maxsus_xot.png"),
        ("Normal kabob", "Обычный шашлык", cat_ids["🍢 Kaboblar"], 18000, "Klassik go'shtli kabob", "Классический мясной шашлык", "images/Normal_kabab.jpg"),
        ("Limon choy", "Лимонный чай", cat_ids["☕️ Ichimliklar"], 5000, "Issiq limon choy", "Горячий лимонный чай", "images/limon_choy.png"),
    ]
    
    for uz, ru, cat_id, price, desc_uz, desc_ru, image in products:
        await db.conn.execute("""
            INSERT INTO product (name_uz, name_ru, category_id, price, description_uz, description_ru, image, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (uz, ru, cat_id, price, desc_uz, desc_ru, image))
    
    await db.conn.commit()
    print("Database seeded with REAL images!")
    await db.close()

if __name__ == "__main__":
    asyncio.run(seed())
