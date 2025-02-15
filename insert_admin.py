import psycopg2
from werkzeug.security import generate_password_hash

# Replace these with your Supabase credentials
DB_HOST = "db.xnhvhzxfsymkloeujjqn.supabase.co"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "Mpkumar98&^"
DB_PORT = "5432"

# Create the admin users
def insert_admins():
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
        
        # Admin users to add
        admin_users = [
            ('purushottam', 'Mpkumar98&^'),
            ('nimda', 'nimda123')
        ]
        
        for username, password in admin_users:
            # Generate hashed password
            hashed_password = generate_password_hash(password)
            
            # Insert admin user
            cur.execute("""
                INSERT INTO "user" (username, password, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (username) 
                DO UPDATE SET password = EXCLUDED.password
                RETURNING id;
            """, (username, hashed_password, 'admin'))
            
            # Commit the transaction
            conn.commit()
            
            # Get the result
            result = cur.fetchone()
            if result:
                print(f"Admin user {username} created/updated successfully with ID:", result[0])
            else:
                print(f"Failed to create/update admin user {username}")
        
        # Close cursor and connection
        cur.close()
        conn.close()
        print("All admin users processed successfully!")
        
    except Exception as e:
        print("Error:", str(e))

if __name__ == "__main__":
    insert_admins()
