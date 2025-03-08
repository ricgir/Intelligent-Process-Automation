import psycopg2
from psycopg2 import errors

def insert_invoice(data, db_config):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        query = """
        INSERT INTO invoices (invoice_number, invoice_date, due_date, vendor_name, customer_name, subtotal, taxes, total_amount, payment_terms)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        values = (
            data.get("invoice_number"),
            data.get("invoice_date"),
            data.get("due_date"),
            data.get("vendor_name"),
            data.get("customer_name"),
            data.get("subtotal"),
            data.get("taxes"),
            data.get("total_amount"),
            data.get("payment_terms"),
        )

        cursor.execute(query, values)
        conn.commit()

    except errors.UniqueViolation:
        return "Error: Duplicate Invoice. Invoice number already exists."
    
    except Exception as e:
        return f"Database Error: {str(e)}"
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return "Success"




