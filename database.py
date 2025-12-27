import datetime
import aiosqlite
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    async def connect(self):
        """Initialize connection and create tables"""
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.db_name)
            self.conn.row_factory = aiosqlite.Row
            await self.create_tables()

    async def close(self):
        """Close connection"""
        if self.conn:
            await self.conn.close()
            self.conn = None

    async def create_tables(self):
        """Create all necessary tables if they don't exist"""
        async with self.conn.cursor() as cur:
            # User table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS user (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER UNIQUE NOT NULL,
                    first_name TEXT,
                    last_name TEXT,
                    lang_id INTEGER,
                    phone_number TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Category table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS category (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_uz TEXT NOT NULL,
                    name_ru TEXT NOT NULL,
                    parent_id INTEGER,
                    FOREIGN KEY (parent_id) REFERENCES category (id)
                )
            """)

            # Product table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS product (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_uz TEXT NOT NULL,
                    name_ru TEXT NOT NULL,
                    category_id INTEGER NOT NULL,
                    price INTEGER NOT NULL,
                    description_uz TEXT,
                    description_ru TEXT,
                    image TEXT,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (category_id) REFERENCES category (id)
                )
            """)

            # Order table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS "order" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    status INTEGER DEFAULT 1,
                    payment_type TEXT,
                    longitude REAL,
                    latitude REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user (id)
                )
            """)

            # OrderProduct table
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS order_product (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES "order" (id),
                    FOREIGN KEY (product_id) REFERENCES product (id)
                )
            """)
            await self.conn.commit()

    async def create_user(self, chat_id):
        """Create a new user"""
        try:
            await self.conn.execute("""INSERT INTO user(chat_id) VALUES (?)""", (chat_id,))
            await self.conn.commit()
        except aiosqlite.IntegrityError:
            pass # User already exists

    async def update_user_data(self, chat_id, key, value):
        """Update user data with key validation to prevent SQL Injection"""
        allowed_keys = {"first_name", "last_name", "lang_id", "phone_number"}
        if key not in allowed_keys:
            logger.error(f"Attempted unauthorized update on key: {key}")
            raise ValueError(f"Unauthorized key: {key}")

        await self.conn.execute(f"UPDATE user SET {key} = ? WHERE chat_id = ?", (value, chat_id))
        await self.conn.commit()

    async def get_user_by_chat_id(self, chat_id):
        """Get user by chat_id"""
        async with self.conn.execute("SELECT * FROM user WHERE chat_id = ?", (chat_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_categories_by_parent(self, parent_id=None):
        """Get categories by parent_id"""
        if parent_id:
            query = "SELECT * FROM category WHERE parent_id = ?"
            params = (parent_id,)
        else:
            query = "SELECT * FROM category WHERE parent_id IS NULL"
            params = ()

        async with self.conn.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_category_parent(self, category_id):
        """Get parent category"""
        async with self.conn.execute("SELECT parent_id FROM category WHERE id = ?", (category_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_products_by_category(self, category_id):
        """Get all products in a category"""
        async with self.conn.execute("SELECT * FROM product WHERE category_id = ? AND is_active = 1", (category_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_product_by_id(self, product_id):
        """Get product by id"""
        async with self.conn.execute("SELECT * FROM product WHERE id = ?", (product_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_products_for_cart(self, product_id):
        """Get product with category info for cart display"""
        query = """
            SELECT product.*, 
                   category.name_uz as cat_name_uz, 
                   category.name_ru as cat_name_ru
            FROM product
            INNER JOIN category ON product.category_id = category.id
            WHERE product.id = ?
        """
        async with self.conn.execute(query, (product_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def create_order(self, user_id, products, payment_type, location):
        """Create a new order with products"""
        # Insert order
        cursor = await self.conn.execute("""
            INSERT INTO "order"(user_id, status, payment_type, longitude, latitude, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, 1, payment_type, location.longitude, location.latitude, datetime.datetime.now()))
        
        last_order_id = cursor.lastrowid

        # Insert order products
        for product_id, amount in products.items():
            await self.conn.execute("""
                INSERT INTO order_product (product_id, order_id, amount, created_at)
                VALUES (?, ?, ?, ?)
            """, (int(product_id), last_order_id, int(amount), datetime.datetime.now()))

        await self.conn.commit()
        return last_order_id

    async def get_user_orders(self, user_id):
        """Get all active orders for a user"""
        async with self.conn.execute("SELECT * FROM \"order\" WHERE user_id = ? AND status = 1", (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_order_products(self, order_id):
        """Get all products in an order"""
        query = """
            SELECT op.*, 
                   p.name_uz as product_name_uz, 
                   p.name_ru as product_name_ru, 
                   p.price   as product_price, 
                   p.image   as product_image
            FROM order_product op
            INNER JOIN product p ON op.product_id = p.id
            WHERE op.order_id = ?
        """
        async with self.conn.execute(query, (order_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_order_by_id(self, order_id):
        """Get order by id"""
        async with self.conn.execute("SELECT * FROM \"order\" WHERE id = ?", (order_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_order_status(self, order_id, status):
        """Update order status"""
        await self.conn.execute("UPDATE \"order\" SET status = ? WHERE id = ?", (status, order_id))
        await self.conn.commit()
