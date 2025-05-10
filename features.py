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
    # customer_id: {C:{C,P}, P:{C,P}} (Customer's identifier, relevant to C and P)
    # offer_id: {Offer:{⊥}, C:{C,P}, P:{C,P}} (ID of a public offer, relevant to C and P in this transaction)
    # shipping_address: {C:{C,P}, P:{C,P}} (Customer's private address, shared with P for this transaction)
    with connect() as conn:
        cursor = conn.cursor()
        # Fetch customer details. Effective readers for DB operation: {P}
        cursor.execute("SELECT name, opt_in FROM Customers WHERE customer_id = ?", (customer_id,))
        customer_data = cursor.fetchone()
        # customer_data (name, opt_in): {C:{C,P}, P:{C,P}} (Data about C, accessible to P)
        if not customer_data:
            raise ValueError("Customer does not exist")
        customer_name, opt_in = customer_data
        
        # customer_name: {C:{C,P}, P:{C,P}}
        # opt_in: {C:{C,P}, P:{C,P}}

        # Fetch offer details. Effective readers for DB operation: {P}
        cursor.execute("SELECT vendor_id, title, price FROM Book_Offers WHERE offer_id = ?", (offer_id,))
        offer = cursor.fetchone()
       
        # offer (vendor_id, title, original_price): {Offer:{⊥}} (Public offer data)
        if not offer:
            raise ValueError("Offer does not exist")
        vendor_id, book_title, original_price = offer
        
        # vendor_id: {V:{⊥}, Offer:{⊥}} (Vendor ID from public offer, relevant to V)
        # book_title: {Offer:{⊥}}
        # original_price: {Offer:{⊥}}
        
        # Calculate price.
        # opt_in: {C:{C,P}, P:{C,P}}
        # original_price: {Offer:{⊥}}
        price = original_price * 0.95 if opt_in else original_price
        # price: {C:{C,P}, P:{C,P}} (Derived, depends on C's opt_in status)
        purchase_date = date.today()

        # purchase_date: {Global:{⊥}} (Publicly known date)

        # Initial label for shipping_address in Purchases. Defines read access.
        # Stored label's content implies initial readers {C, P} for shipping_address.
        label = {"read_by": [str(customer_id), "platform"], "write_by": [str(customer_id)]}
        # label (dict variable): {P:{P}} (Platform internal data structure)
        label_str = json.dumps(label)

        # label_str (JSON string representation of the label): {P:{P}}

        # Insert purchase. Effective writer for DB operation: {P}
        # shipping_address ({C:{C,P}, P:{C,P}}) is stored with label_str.
        cursor.execute(
            "INSERT INTO Purchases (customer_id, offer_id, shipping_address, shipping_address_label, purchase_date) VALUES (?, ?, ?, ?, ?)",
            (customer_id, offer_id, shipping_address, label_str, purchase_date)
        )
        purchase_id = cursor.lastrowid
        
        # purchase_id: {P:{P}} (DB generated ID, known to P)
        # Prepare an updated label for shipping_address.
        new_label = label.copy()
        # vendor_id ({V:{⊥}, Offer:{⊥}}) is public.
        new_label["read_by"].append(str(vendor_id))
        # Updated label content implies readers {C, P, V} for shipping_address

        # opt_in: {C:{C,P}, P:{C,P}}
        if opt_in:
            # Add M to readers of shipping_address
            new_label["read_by"].append("marketing")
            # Updated label content implies readers {C, P, V, M} for shipping_address
            # price: {C:{C,P}, P:{C,P}}
            print(f"Customer opted in for marketing data sharing. Price reduced to ${price:.2f} (5% discount).")
        
        new_label_str = json.dumps(new_label)
        # Update label in DB. Effective writer for DB operation: {P}
        cursor.execute("UPDATE Purchases SET shipping_address_label = ? WHERE purchase_id = ?", (new_label_str, purchase_id))
        
        # Principals for access check. These are platform's representations.
        vendor = Principal(str(vendor_id))
        marketing = Principal("marketing")

        # Retrieve stored label. Effective reader for DB operation: {P}
        cursor.execute("SELECT shipping_address_label FROM Purchases WHERE purchase_id = ?", (purchase_id,))
        row = cursor.fetchone()
        # row[0] contains the JSON policy string for shipping_address.

        # Construct confirmations. Platform (P) creates these strings.
        # Disclosure of shipping_address ({C:{C,P}, P:{C,P}}) is conditional on policy in row[0].
        # customer_name: {C:{C,P}, P:{C,P}}
        confirmation_vendor = (
            f"Purchase confirmed! Customer: {customer_name}, Shipping Address: {shipping_address}"
            if row and vendor.can_read(row[0]) else
            f"Purchase confirmed! Customer: {customer_name}, but you don't have access to shipping address."
        )

        # confirmation_vendor (string): {P:{P}}. Information revealed to V is customer_name; shipping_address if permitted by policy.
        
        # book_title: {Offer:{⊥}}
        confirmation_marketing = (
            f"Marketing data received: Customer {customer_name} bought '{book_title}' at {shipping_address}"
            if row and marketing.can_read(row[0]) else
            "No marketing data shared."
        )

        # confirmation_marketing (string): {P:{P}}. Information revealed to M is customer_name, book_title; shipping_address if permitted.
        
        # get_vendor_name(vendor_id) -> vendor_name: {V:{⊥}, P:{⊥}} (public name, relevant to V and P context)
        # book_title: {Offer:{⊥}}
        # price: {C:{C,P}, P:{C,P}}
        confirmation_customer = f"Purchase confirmed! Vendor: {get_vendor_name(vendor_id)}, Book: {book_title}, Price: ${price:.2f}"
        # confirmation_customer (string): {P:{P}}. Information revealed to C.
        
        # Output by P
        print("Confirmation for vendor:", confirmation_vendor)
        print("Confirmation for marketing:", confirmation_marketing)
        print("Confirmation for customer:", confirmation_customer)
    return "Purchase completed successfully"
