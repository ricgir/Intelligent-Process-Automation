import psycopg2

def insert_invoice(data, db_config):
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()  # ✅ Ensure cursor is initialized

        # SQL query
        query = """
        INSERT INTO invoices (invoice_number, invoice_date, due_date, vendor_name, customer_name, subtotal, taxes, total_amount, payment_terms)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        # Extract values from dictionary
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

        # Execute query
        cursor.execute(query, values)
        conn.commit()

    except Exception as e:
        print("Error:", e)

    finally:
        if 'cursor' in locals():  # ✅ Ensure cursor exists before closing
            cursor.close()
        if 'conn' in locals():
            conn.close()
