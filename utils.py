from database import connect

def get_customer_name(customer_id):
    """Retrieve a customer's name by ID."""
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Customers WHERE customer_id = ?", (customer_id,))
        row = cursor.fetchone()
        return row[0] if row else None

def get_vendor_name(vendor_id):
    """Retrieve a vendor's name by ID."""
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Vendors WHERE vendor_id = ?", (vendor_id,))
        row = cursor.fetchone()
        return row[0] if row else None