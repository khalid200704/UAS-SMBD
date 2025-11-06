from database import get_connection
import bcrypt

def check_users_table():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    
    try:
        # Check if users table exists and get its structure
        cur.execute("SHOW TABLES LIKE 'users'")
        if not cur.fetchone():
            print("Error: 'users' table does not exist!")
            return
            
        # Get all users
        cur.execute('SELECT id, username, password FROM users')
        users = cur.fetchall()
        
        if not users:
            print("No users found in the database!")
            return
            
        print("\nCurrent users in database:")
        print("-" * 50)
        print(f"{'ID':<5} | {'Username':<15} | Password Hash Status")
        print("-" * 50)
        
        for user in users:
            password = user['password']
            is_hashed = password.startswith('$2b$')
            status = "✅ Hashed (bcrypt)" if is_hashed else "❌ Not Hashed (plaintext)"
            print(f"{user['id']:<5} | {user['username']:<15} | {status}")
            
    except Exception as e:
        print(f"Error accessing database: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("Checking users table...")
    check_users_table()
