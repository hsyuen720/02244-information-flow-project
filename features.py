from database import connect
from security import Principal
from utils import get_customer_name, get_vendor_name
import json
from datetime import date

def offer(vendor_id, **book_details):
    """
    Allow a vendor to offer a book for sale.
    
    Security Label: {"read_by": ["public"], "write_by": [vendor_id, "platform"]}
    - Owners: [vendor_id, "platform"]
    - Readers(vendor_id): ["public"], Readers("platform"): ["public"]
    - EffectiveReaders: ["public"]
    - Writers: [vendor_id, "platform"]
    - Ordering (⊑): Less restrictive, lower in the lattice.
    """
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Vendors WHERE vendor_id = ?", (vendor_id,))
        if not cursor.fetchone():
            raise ValueError("Vendor does not exist")
        keys = list(book_details.keys())
        values = tuple(book_details.values())
        placeholders = ','.join(['?'] * len(keys))
        sql = f"INSERT INTO Book_Offers (vendor_id, {','.join(keys)}) VALUES (?, {placeholders})"
        cursor.execute(sql, (vendor_id,) + values)
    return "Offer added successfully"

def search(customer_id, **search_query):
    """
    Allow a customer to search for books.
    
    Security Label for search query: {"read_by": [customer_id, "platform"], "write_by": [customer_id]}
    - Owners: [customer_id]
    - Readers(customer_id): [customer_id, "platform"]
    - EffectiveReaders: [customer_id, "platform"]
    - Writers: [customer_id]
    - Ordering (⊑): More restrictive, higher in the lattice.
    """
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Customers WHERE customer_id = ?", (customer_id,))
        if not cursor.fetchone():
            raise ValueError("Customer does not exist")
        conditions = [f"{key} LIKE ?" for key in search_query]
        values = [f"%{value}%" for value in search_query.values()]
        sql = f"SELECT * FROM Book_Offers WHERE {' AND '.join(conditions)}"
        cursor.execute(sql, tuple(values))
        return cursor.fetchall()

def purchase(customer_id, offer_id, shipping_address):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, opt_in FROM Customers WHERE customer_id = ?", (customer_id,))
        customer_data = cursor.fetchone()
        if not customer_data:
            raise ValueError("Customer does not exist")
        customer_name, opt_in = customer_data
        
        cursor.execute("SELECT vendor_id, title, price FROM Book_Offers WHERE offer_id = ?", (offer_id,))
        offer = cursor.fetchone()
        if not offer:
            raise ValueError("Offer does not exist")
        vendor_id, book_title, original_price = offer
        
        price = original_price * 0.95 if opt_in else original_price
        
        purchase_date = date.today()
        label = {"read_by": [str(customer_id), "platform"], "write_by": [str(customer_id)]}
        label_str = json.dumps(label)
        cursor.execute(
            "INSERT INTO Purchases (customer_id, offer_id, shipping_address, shipping_address_label, purchase_date) VALUES (?, ?, ?, ?, ?)",
            (customer_id, offer_id, shipping_address, label_str, purchase_date)
        )
        purchase_id = cursor.lastrowid
        
        new_label = label.copy()
        new_label["read_by"].append(str(vendor_id))
        
        if opt_in:
            new_label["read_by"].append("marketing")
            print(f"Customer opted in for marketing data sharing. Price reduced to ${price:.2f} (5% discount).")
        
        new_label_str = json.dumps(new_label)
        cursor.execute("UPDATE Purchases SET shipping_address_label = ? WHERE purchase_id = ?", (new_label_str, purchase_id))
        
        vendor = Principal(str(vendor_id))
        marketing = Principal("marketing")
        cursor.execute("SELECT shipping_address_label FROM Purchases WHERE purchase_id = ?", (purchase_id,))
        row = cursor.fetchone()
        
        confirmation_vendor = (
            f"Purchase confirmed! Customer: {customer_name}, Shipping Address: {shipping_address}"
            if row and vendor.can_read(row[0]) else
            f"Purchase confirmed! Customer: {customer_name}, but you don't have access to shipping address."
        )
        confirmation_marketing = (
            f"Marketing data received: Customer {customer_name} bought '{book_title}' at {shipping_address}"
            if row and marketing.can_read(row[0]) else
            "No marketing data shared."
        )
        confirmation_customer = f"Purchase confirmed! Vendor: {get_vendor_name(vendor_id)}, Book: {book_title}, Price: ${price:.2f}"
        
        print("Confirmation for vendor:", confirmation_vendor)
        print("Confirmation for marketing:", confirmation_marketing)
        print("Confirmation for customer:", confirmation_customer)
    return "Purchase completed successfully"