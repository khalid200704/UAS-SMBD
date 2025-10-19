import mysql.connector

def update_database():
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="yolo_edge"
        )
        cursor = conn.cursor()
        
        # Add human_count column if not exists
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'yolo_edge' 
            AND TABLE_NAME = 'detections' 
            AND COLUMN_NAME = 'human_count'""")
            
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                ALTER TABLE detections 
                ADD COLUMN human_count INT DEFAULT 0 
                AFTER delay_ms""")
            print("✅ Successfully added 'human_count' column to 'detections' table")
        else:
            print("ℹ️ 'human_count' column already exists in 'detections' table")
        
        conn.commit()
        print("✅ Database schema updated successfully!")
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    print("🔄 Updating database schema...")
    update_database()
    print("✅ Update process completed!")
