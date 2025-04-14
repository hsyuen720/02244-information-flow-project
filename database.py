import sqlite3

def connect():
    """Establish a connection to the book marketplace database."""
    return sqlite3.connect("book_marketplace.db")

def setup_database():
    """Set up the database tables and insert initial data."""
    with connect() as conn:
        cursor = conn.cursor()
        # Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT,
                address TEXT,
                address_label TEXT,
                opt_in BOOLEAN,
                opt_in_label TEXT
            )
        """)
        # Vendors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Vendors (
                vendor_id INTEGER PRIMARY KEY,
                name TEXT,
                contact TEXT
            )
        """)
        # Book Offers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Book_Offers (
                offer_id INTEGER PRIMARY KEY,
                vendor_id INTEGER,
                title TEXT,
                author TEXT,
                year INTEGER,
                edition TEXT,
                publisher TEXT,
                condition TEXT,
                description TEXT,
                price REAL
            )
        """)
        # Purchases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Purchases (
                purchase_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                offer_id INTEGER,
                shipping_address TEXT,
                shipping_address_label TEXT,
                purchase_date DATE
            )
        """)

        cursor.execute("""
            INSERT OR IGNORE INTO Customers (customer_id, name, address, address_label, opt_in, opt_in_label)
            VALUES (1, 'John Doe', '123 Main St', '{"read_by": ["1", "platform"], "write_by": ["1"]}', 1, '{"read_by": ["1", "platform"], "write_by": ["1"]}')
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO Vendors (vendor_id, name, contact)
            VALUES (1, 'Bookstore Inc.', 'contact@bookstore.com')
        """)
        cursor.execute("""
            INSERT OR IGNORE INTO Book_Offers (offer_id, vendor_id, title, author, year, edition, publisher, condition, description, price)
            VALUES (1, 1, 'Classic Novel', 'Author Name', 2000, 'First Edition', 'Publisher Name', 'Good', 'A great book.', 19.99)
        """)