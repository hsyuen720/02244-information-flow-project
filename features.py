from database import connect
from security import Principal
from utils import get_customer_name, get_vendor_name
import json
from datetime import date

def offer(vendor_id, **book_details):
    with connect() as conn:
        cursor = conn.cursor()

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

        if vendor_name is None:
            raise ValueError("Vendor does not exist")

        # if Book_Offers is none， set a default vendor_name
        cursor.execute("PRAGMA table_info(Book_Offers)")
        cols = [col[1] for col in cursor.fetchall()]
        if "vendor_name" not in cols:
            cursor.execute("ALTER TABLE Book_Offers ADD COLUMN vendor_name TEXT")

        # insert vendor_name into book_details，and sql
        book_details = dict(book_details)
        book_details["vendor_name"] = vendor_name

        keys         = list(book_details.keys())
        placeholders = ",".join("?" for _ in keys)
        sql = f"""
            INSERT INTO Book_Offers (vendor_id,{','.join(keys)})
            VALUES (?,{placeholders})
        """
        cursor.execute(sql, (vendor_id, *book_details.values()))
    return "Offer added successfully"


def search(customer_id: int, **search_query):
    """
    Let a customer search public book offers.

    Security spec (Myers DLM):
        • Label(input search_query) = {read_by:[customer_id,"platform"],
                                       write_by:[customer_id]}
        • Label(output)             = {read_by:["public"],
                                       write_by:["platform"]}
        No declassification needed (only public data involved).
    """

    # Whitelist of allowed fields — Only search and return these columns
    allowed_fields = {
        "title", "author", "year", "edition", "publisher",
        "condition", "description", "price", "vendor_name"
    }

    with connect() as conn:
        cur = conn.cursor()

        # Verify that the customer exists
        if cur.execute("SELECT 1 FROM Customers WHERE customer_id=?",
                       (customer_id,)).fetchone() is None:
            raise ValueError("Customer does not exist")

        # Check that all search fields are valid
        for k in search_query:
            if k not in allowed_fields:
                raise ValueError(f"Illegal search field: {k}")

        # Build the WHERE clause (vendor_name needs a JOIN)
        conds, vals = [], []
        for k, v in search_query.items():
            if k == "vendor_name":
                conds.append("v.name LIKE ?")
            else:
                conds.append(f"o.{k} LIKE ?")
            vals.append(f"%{v}%")
        where_sql = " WHERE " + " AND ".join(conds) if conds else ""

        # Query only public columns — vendor_name comes from v.name
        select_cols = """
            o.title, o.author, o.year, o.edition, o.publisher,
            o.condition, o.description, o.price,
            v.name AS vendor_name
        """
        sql = f"""
            SELECT {select_cols}
            FROM Book_Offers AS o
            JOIN Vendors AS v ON o.vendor_id = v.vendor_id
            {where_sql}
        """
        cur.execute(sql, tuple(vals))
        rows = cur.fetchall()

    # Package the results with the public security label
    col_names = [
        "title", "author", "year", "edition", "publisher",
        "condition", "description", "price", "vendor_name"
    ]
    public_label = {"read_by": ["public"], "write_by": ["platform"]}
    return [{"data": dict(zip(col_names, row)),
             "label": json.dumps(public_label)} for row in rows]


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
