import datetime
import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False, timeout=10)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Create all necessary tables if they don't exist"""

        # User table
        self.cur.execute("""
                         CREATE TABLE IF NOT EXISTS user
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             chat_id
                             INTEGER
                             UNIQUE
                             NOT
                             NULL,
                             first_name
                             TEXT,
                             last_name
                             TEXT,
                             lang_id
                             INTEGER,
                             phone_number
                             TEXT,
                             created_at
                             DATETIME
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         """)

        # Category table
        self.cur.execute("""
                         CREATE TABLE IF NOT EXISTS category
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             name_uz
                             TEXT
                             NOT
                             NULL,
                             name_ru
                             TEXT
                             NOT
                             NULL,
                             parent_id
                             INTEGER,
                             FOREIGN
                             KEY
                         (
                             parent_id
                         ) REFERENCES category
                         (
                             id
                         )
                             )
                         """)

        # Product table
        self.cur.execute("""
                         CREATE TABLE IF NOT EXISTS product
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             name_uz
                             TEXT
                             NOT
                             NULL,
                             name_ru
                             TEXT
                             NOT
                             NULL,
                             category_id
                             INTEGER
                             NOT
                             NULL,
                             price
                             INTEGER
                             NOT
                             NULL,
                             description_uz
                             TEXT,
                             description_ru
                             TEXT,
                             image
                             TEXT,
                             is_active
                             INTEGER
                             DEFAULT
                             1,
                             FOREIGN
                             KEY
                         (
                             category_id
                         ) REFERENCES category
                         (
                             id
                         )
                             )
                         """)

        # Order table (with quotes because 'order' is SQL keyword)
        self.cur.execute("""
                         CREATE TABLE IF NOT EXISTS "order"
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             user_id
                             INTEGER
                             NOT
                             NULL,
                             status
                             INTEGER
                             DEFAULT
                             1,
                             payment_type
                             TEXT,
                             longitude
                             REAL,
                             latitude
                             REAL,
                             created_at
                             DATETIME
                             DEFAULT
                             CURRENT_TIMESTAMP,
                             FOREIGN
                             KEY
                         (
                             user_id
                         ) REFERENCES user
                         (
                             id
                         )
                             )
                         """)

        # OrderProduct table
        self.cur.execute("""
                         CREATE TABLE IF NOT EXISTS order_product
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             order_id
                             INTEGER
                             NOT
                             NULL,
                             product_id
                             INTEGER
                             NOT
                             NULL,
                             amount
                             INTEGER
                             NOT
                             NULL,
                             created_at
                             DATETIME
                             DEFAULT
                             CURRENT_TIMESTAMP,
                             FOREIGN
                             KEY
                         (
                             order_id
                         ) REFERENCES "order"
                         (
                             id
                         ),
                             FOREIGN KEY
                         (
                             product_id
                         ) REFERENCES product
                         (
                             id
                         )
                             )
                         """)

        self.conn.commit()

    def create_user(self, chat_id):
        """Create a new user"""
        self.cur.execute("""INSERT INTO user(chat_id)
                            VALUES (?)""", (chat_id,))
        self.conn.commit()

    def update_user_data(self, chat_id, key, value):
        """Update user data"""
        self.cur.execute(f"""UPDATE user SET {key} = ? WHERE chat_id = ?""", (value, chat_id))
        self.conn.commit()

    def get_user_by_chat_id(self, chat_id):
        """Get user by chat_id"""
        self.cur.execute("""SELECT *
                            FROM user
                            WHERE chat_id = ?""", (chat_id,))
        user = dict_fetchone(self.cur)
        return user

    def get_categories_by_parent(self, parent_id=None):
        """Get categories by parent_id"""
        if parent_id:
            self.cur.execute("""SELECT *
                                FROM category
                                WHERE parent_id = ?""", (parent_id,))
        else:
            self.cur.execute("""SELECT *
                                FROM category
                                WHERE parent_id IS NULL""")

        categories = dict_fetchall(self.cur)
        return categories

    def get_category_parent(self, category_id):
        """Get parent category"""
        self.cur.execute("""SELECT parent_id
                            FROM category
                            WHERE id = ?""", (category_id,))
        category = dict_fetchone(self.cur)
        return category

    def get_products_by_category(self, category_id):
        """Get all products in a category"""
        self.cur.execute("""SELECT *
                            FROM product
                            WHERE category_id = ?
                              AND is_active = 1""", (category_id,))
        products = dict_fetchall(self.cur)
        return products

    def get_product_by_id(self, product_id):
        """Get product by id"""
        self.cur.execute("""SELECT *
                            FROM product
                            WHERE id = ?""", (product_id,))
        product = dict_fetchone(self.cur)
        return product

    def get_products_for_cart(self, product_id):
        """Get product with category info for cart display"""
        self.cur.execute("""
                         SELECT product.*,
                                category.name_uz as cat_name_uz,
                                category.name_ru as cat_name_ru
                         FROM product
                                  INNER JOIN category ON product.category_id = category.id
                         WHERE product.id = ?
                         """, (product_id,))
        product = dict_fetchone(self.cur)
        return product

    def create_order(self, user_id, products, payment_type, location):
        """Create a new order with products"""
        # Insert order
        self.cur.execute("""
                         INSERT INTO "order"(user_id, status, payment_type, longitude, latitude, created_at)
                         VALUES (?, ?, ?, ?, ?, ?)
                         """,
                         (user_id, 1, payment_type, location.longitude, location.latitude, datetime.datetime.now()))
        self.conn.commit()

        # Get last inserted order id
        last_order_id = self.cur.lastrowid

        # Insert order products
        for product_id, amount in products.items():
            self.cur.execute("""
                             INSERT INTO order_product (product_id, order_id, amount, created_at)
                             VALUES (?, ?, ?, ?)
                             """, (int(product_id), last_order_id, int(amount), datetime.datetime.now()))

        self.conn.commit()
        return last_order_id

    def get_user_orders(self, user_id):
        """Get all active orders for a user"""
        self.cur.execute("""SELECT *
                            FROM "order"
                            WHERE user_id = ?
                              AND status = 1""", (user_id,))
        orders = dict_fetchall(self.cur)
        return orders

    def get_order_products(self, order_id):
        """Get all products in an order"""
        self.cur.execute("""
                         SELECT op.*,
                                p.name_uz as product_name_uz,
                                p.name_ru as product_name_ru,
                                p.price   as product_price,
                                p.image   as product_image
                         FROM order_product op
                                  INNER JOIN product p ON op.product_id = p.id
                         WHERE op.order_id = ?
                         """, (order_id,))
        products = dict_fetchall(self.cur)
        return products

    def get_order_by_id(self, order_id):
        """Get order by id"""
        self.cur.execute("""SELECT *
                            FROM "order"
                            WHERE id = ?""", (order_id,))
        order = dict_fetchone(self.cur)
        return order

    def update_order_status(self, order_id, status):
        """Update order status"""
        self.cur.execute("""UPDATE "order"
                            SET status = ?
                            WHERE id = ?""", (status, order_id))
        self.conn.commit()


def dict_fetchall(cursor):
    """Convert cursor results to list of dictionaries"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def dict_fetchone(cursor):
    """Convert cursor result to dictionary"""
    row = cursor.fetchone()
    if row is None:
        return False
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))