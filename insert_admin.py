import psycopg2
from werkzeug.security import generate_password_hash

# Replace these with your Supabase credentials
DB_HOST = "db.xnhvhzxfsymkloeujjqn.supabase.co"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "YOUR-PASSWORD-HERE"
DB_PORT = "5432"

# Create the admin user
def insert_admin():
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Generate hashed password
        hashed_password = generate_password_hash('Mpkumar98&^')
        
        # Insert admin user
        cur.execute("""
            INSERT INTO "user" (username, password, role)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING
            RETURNING id;
        """, ('purushottam', hashed_password, 'admin'))
        
        # Commit the transaction
        conn.commit()
        
        # Get the result
        result = cur.fetchone()
        if result:
            print("Admin user created successfully with ID:", result[0])
        else:
            print("Admin user already exists")
        
        # Close cursor and connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    insert_admin()
