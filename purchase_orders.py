from database import get_connection


# ============================================================
# CREATE PURCHASE ORDER
# ============================================================

def create_purchase_order(
    supplier,
    product,
    quantity,
    delivery_location,
    required_delivery_date
):

    connection = get_connection()

    cursor = connection.cursor()


    # --------------------------------------------------------
    # Generate PO number
    # --------------------------------------------------------

    cursor.execute(
        "SELECT COUNT(*) FROM purchase_orders"
    )

    count = cursor.fetchone()[0]

    po_number = f"PO-{count + 1:04d}"


    # --------------------------------------------------------
    # Calculate amount
    # --------------------------------------------------------

    unit_price = float(product["unit_price"])

    total_amount = unit_price * quantity


    # --------------------------------------------------------
    # Save PO
    # --------------------------------------------------------

    cursor.execute("""
        INSERT INTO purchase_orders
        (
            po_number,
            supplier_id,
            supplier_name,
            product_id,
            product_name,
            quantity,
            unit_price,
            total_amount,
            delivery_location,
            required_delivery_date,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        po_number,
        supplier["id"],
        supplier["name"],
        product["id"],
        product["name"],
        quantity,
        unit_price,
        total_amount,
        delivery_location,
        required_delivery_date,
        "CREATED"
    ))


    connection.commit()


    po_id = cursor.lastrowid


    cursor.execute("""
        SELECT *
        FROM purchase_orders
        WHERE id = ?
    """, (po_id,))


    purchase_order = cursor.fetchone()


    connection.close()


    return purchase_order


# ============================================================
# GET ALL PURCHASE ORDERS
# ============================================================

def get_purchase_orders():

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM purchase_orders
        ORDER BY id DESC
    """)


    purchase_orders = cursor.fetchall()

    connection.close()

    return purchase_orders


# ============================================================
# GET ONE PURCHASE ORDER
# ============================================================

def get_purchase_order(po_number):

    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute("""
        SELECT *
        FROM purchase_orders
        WHERE po_number = ?
    """, (po_number,))


    purchase_order = cursor.fetchone()

    connection.close()

    return purchase_order


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Purchase Order module loaded successfully."
    )
