import mysql.connector
from datetime import datetime

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",      # ubah sesuai MySQL kamu
        database="yolo_edge"
    )

def insert_detection(device_id, status, jitter, delay, human_count=0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO detections (device_id, timestamp, status, jitter, delay_ms, human_count)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (device_id, datetime.now(), status, jitter, delay, human_count))
    conn.commit()
    cursor.close()
    conn.close()

def update_device(device_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE devices 
        SET total_human_detection = total_human_detection + 1,
            last_status = %s,
            last_active = %s
        WHERE id = %s
    """, (status, datetime.now(), device_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_dashboard_data(device_id: int = 1):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT timestamp, status, jitter, delay_ms AS delay, human_count
        FROM detections 
        ORDER BY timestamp DESC LIMIT 50
    """)
    data = cursor.fetchall()
    
    # Ambil total deteksi dari tabel devices
    cursor.execute("SELECT total_human_detection FROM devices WHERE id = %s", (device_id,))
    device_data = cursor.fetchone()
    total_detections = device_data['total_human_detection'] if device_data else 0
    
    cursor.close()
    conn.close()
    
    # Tambahkan total ke data response
    return {
        'recent_detections': data,
        'total_detections': total_detections
    }
