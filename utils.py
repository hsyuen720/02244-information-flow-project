from database import connect

def get_customer_name(customer_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Customers WHERE customer_id = ?", (customer_id,))
        row = cursor.fetchone()
        return row[0] if row else None

def get_vendor_name(vendor_id):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM Vendors WHERE vendor_id = ?", (vendor_id,))
        row = cursor.fetchone()
        # Get the data on behalf of Vendor and Platform
        # if_acts_for(get_vendor_name, {V,P})
        # vendorName := declassify(vendorName, {V,P:{⊥}})
        return row[0] if row else None