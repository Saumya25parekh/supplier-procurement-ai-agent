import sqlite3


DATABASE_NAME = "procurement.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():

    connection = get_connection()

    cursor = connection.cursor()


    # --------------------------------------------------------
    # SUPPLIERS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT,
            category TEXT,
            rating REAL,
            lead_time_days INTEGER,
            payment_terms TEXT,
            contact_email TEXT,
            active INTEGER DEFAULT 1
        )
    """)


    # --------------------------------------------------------
    # PRODUCTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            specifications TEXT,
            unit_price REAL,
            unit TEXT DEFAULT 'unit'
        )
    """)


    # --------------------------------------------------------
    # PURCHASE ORDERS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            po_number TEXT UNIQUE NOT NULL,
            supplier_id INTEGER NOT NULL,
            supplier_name TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_amount REAL NOT NULL,
            delivery_location TEXT,
            required_delivery_date TEXT,
            status TEXT DEFAULT 'CREATED',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)


    connection.commit()

    connection.close()


# ============================================================
# SAMPLE SUPPLIERS
# ============================================================

def insert_sample_suppliers():

    connection = get_connection()

    cursor = connection.cursor()


    suppliers = [

        (
            "TechSource India",
            "Chennai",
            "Electronics",
            4.7,
            7,
            "Net 30",
            "sales@techsource.example"
        ),

        (
            "Global Devices Pvt Ltd",
            "Bangalore",
            "Electronics",
            4.5,
            10,
            "Net 45",
            "sales@globaldevices.example"
        ),

        (
            "Prime IT Solutions",
            "Hyderabad",
            "Electronics",
            4.2,
            8,
            "Net 30",
            "sales@primeit.example"
        ),

        (
            "Enterprise Tech Supply",
            "Mumbai",
            "Electronics",
            4.8,
            12,
            "Net 60",
            "sales@enterprisetech.example"
        ),

        (
            "South India Computer Systems",
            "Coimbatore",
            "Electronics",
            4.4,
            6,
            "Net 30",
            "sales@sics.example"
        )

    ]


    for supplier in suppliers:

        cursor.execute("""
            INSERT INTO suppliers
            (
                name,
                location,
                category,
                rating,
                lead_time_days,
                payment_terms,
                contact_email
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, supplier)


    connection.commit()

    connection.close()


# ============================================================
# SAMPLE PRODUCTS
# ============================================================

def insert_sample_products():

    connection = get_connection()

    cursor = connection.cursor()


    products = [

        (
            "Business Laptop",
            "Laptops",
            "Windows 11 Pro, 16GB RAM, 512GB SSD",
            65000,
            "unit"
        ),

        (
            "Business Laptop Pro",
            "Laptops",
            "Windows 11 Pro, 16GB RAM, 1TB SSD",
            78000,
            "unit"
        ),

        (
            "Standard Laptop",
            "Laptops",
            "Windows 11 Pro, 8GB RAM, 512GB SSD",
            52000,
            "unit"
        ),

        (
            "Desktop Computer",
            "Computers",
            "Windows 11 Pro, 16GB RAM, 512GB SSD",
            58000,
            "unit"
        ),

        (
            "24-inch Monitor",
            "Monitors",
            "24-inch Full HD IPS",
            12000,
            "unit"
        ),

        (
            "27-inch Monitor",
            "Monitors",
            "27-inch QHD IPS",
            22000,
            "unit"
        ),

        (
            "Wireless Keyboard",
            "Accessories",
            "Wireless USB keyboard",
            1800,
            "unit"
        ),

        (
            "Wireless Mouse",
            "Accessories",
            "Wireless optical mouse",
            900,
            "unit"
        ),

        (
            "USB-C Dock",
            "Accessories",
            "USB-C multi-port docking station",
            7500,
            "unit"
        ),

        (
            "Laptop Backpack",
            "Accessories",
            "Professional laptop backpack",
            2500,
            "unit"
        )

    ]


    for product in products:

        cursor.execute("""
            INSERT INTO products
            (
                name,
                category,
                specifications,
                unit_price,
                unit
            )
            VALUES (?, ?, ?, ?, ?)
        """, product)


    connection.commit()

    connection.close()


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    create_tables()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        "SELECT COUNT(*) FROM suppliers"
    )

    supplier_count = cursor.fetchone()[0]


    cursor.execute(
        "SELECT COUNT(*) FROM products"
    )

    product_count = cursor.fetchone()[0]


    connection.close()


    if supplier_count == 0:

        insert_sample_suppliers()


    if product_count == 0:

        insert_sample_products()


# ============================================================
# GET SUPPLIERS
# ============================================================

def get_suppliers():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM suppliers
        WHERE active = 1
        ORDER BY rating DESC
    """)


    suppliers = cursor.fetchall()

    connection.close()

    return suppliers


# ============================================================
# GET PRODUCTS
# ============================================================

def get_products():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM products
        ORDER BY name
    """)


    products = cursor.fetchall()

    connection.close()

    return products


# ============================================================
# FIND PRODUCT
# ============================================================

def find_product(product_name):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM products
        WHERE LOWER(name) LIKE LOWER(?)
        OR LOWER(category) LIKE LOWER(?)
    """, (
        f"%{product_name}%",
        f"%{product_name}%"
    ))


    products = cursor.fetchall()

    connection.close()

    return products


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    initialize_database()

    print("Database initialized successfully!")

    print("\nSUPPLIERS:")

    for supplier in get_suppliers():

        print(
            f"{supplier['name']} | "
            f"{supplier['location']} | "
            f"Rating: {supplier['rating']} | "
            f"Lead time: {supplier['lead_time_days']} days"
        )


    print("\nPRODUCTS:")

    for product in get_products():

        print(
            f"{product['name']} | "
            f"{product['category']} | "
            f"₹{product['unit_price']}"
        )
