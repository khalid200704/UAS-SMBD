import bcrypt
from database import get_connection

def hash_existing_passwords():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all users with plaintext passwords
    cursor.execute("SELECT id, username, password FROM users")
    users = cursor.fetchall()
    
    updated = 0
    for user in users:
        # Skip already hashed passwords
        if user['password'].startswith('$2b$'):
            continue
            
        # Hash the password
        hashed = bcrypt.hashpw(user['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Update the user with hashed password
        update_cursor = conn.cursor()
        update_cursor.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (hashed.decode('utf-8'), user['id'])
        )
        update_cursor.close()
        
        print(f"Updated password for user: {user['username']}")
        updated += 1
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"\nSuccessfully updated {updated} user(s)")

if __name__ == "__main__":
    print("Starting password hashing process...")
    hash_existing_passwords()
