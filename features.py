from database import connect
from security import Principal
from utils import get_customer_name, get_vendor_name
import json
from datetime import date

def offer(vendor_id, **book_details):
    with connect() as conn:
        cursor = conn.cursor()
        # vendor_id: {V:{V、P}, P:{V、P}}
        # get vendor_name
        # returns None {}
        # vendor Restriction : vendor : {V:{V、P}, P:{V、P}}
        # effective readers: {V、P}
        # if_acts_for(offer, {C、V、P}):
        # vendor := declassify(vendor, {V:{C、V、P}, P:{C、V、P}，C:{C、V、P}})
        # effective readers: {C、V、P}
        # We can find out that everyone can read it is actually equivalent to the {⊥}
        # Here, we get name by their id

        vendor_name = get_vendor_name(vendor_id)
        # vendor_name: {V:{⊥}, P:{⊥}}
        if vendor_name is None:
            raise ValueError("Vendor does not exist")
        # vendor_name: {V:{⊥}, P:{⊥}}
        # The vendor name opinion is declassified so it can be used for lookups without compromising security.
        cursor.execute("PRAGMA table_info(Book_Offers)")
        cols = [col[1] for col in cursor.fetchall()]
        if "vendor_name" not in cols:
            cursor.execute("ALTER TABLE Book_Offers ADD COLUMN vendor_name TEXT")

        book_details = dict(book_details)
        # bvendor_name : {V:{⊥}, P:{⊥}}
        # book_details: {V:{⊥}, P:{⊥}}
        book_details["vendor_name"] = vendor_name
        # book_details : {V:{⊥}, P:{⊥}}
        keys= list(book_details.keys())
        placeholders = ",".join("?" for _ in keys)
        sql = f"""
            INSERT INTO Book_Offers (vendor_id,{','.join(keys)})
            VALUES (?,{placeholders})
        """
        cursor.execute(sql, (vendor_id, *book_details.values()))
    return "Offer added successfully"

def search(customer_id, **search_query):
    """
        customer_id   : {C:{C, P}, P:{C, P}}
        search_query  : {C:{C, P}, P:{C, P}}
        rows (result) : {C:{⊥}, P:{⊥}}
    """
    with connect() as conn:
        cursor = conn.cursor()

        # customer_id: {C:{C, P}, P:{C,P}}
        # effective readers: {C,P}
        cursor.execute("SELECT 1 FROM Customers WHERE customer_id = ?", (customer_id,))
        if not cursor.fetchone():
            raise ValueError("Customer does not exist")

        # search_query: {C:{C, P}, P:{C, P}}
        # effective readers: {C, P}
        if search_query:
            conditions = [f"{k} LIKE ?" for k in search_query]
            values     = [f"%{v}%" for v in search_query.values()]
            sql = f"""SELECT offer_id, title, author, year, edition, publisher, condition, description, price FROM Book_Offers WHERE {' AND '.join(conditions)} """
            cursor.execute(sql, tuple(values))
        else:
            cursor.execute("""SELECT offer_id, title, author, year, edition, publisher, condition, description, price FROM Book_Offers """)

        # rows: {C:{⊥}, P:{⊥}}
        # effective readers: {⊥}
        rows = cursor.fetchall()

    return rows


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
