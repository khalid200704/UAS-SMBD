import mysql.connector
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'yolo_edge')
    )

def insert_detection(device_id, status, jitter, delay, human_count):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO detections (device_id, status, jitter, delay_ms, human_count, timestamp)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """, (device_id, status, jitter, delay, human_count))
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
            last_active = NOW()
        WHERE id = %s
    """, (status, device_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_dashboard_data(device_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Ambil 10 deteksi terbaru
    cursor.execute("""
        SELECT timestamp, status, delay_ms as delay, jitter, human_count
        FROM detections
        WHERE device_id = %s
        ORDER BY timestamp DESC
        LIMIT 10
    """, (device_id,))
    recent = cursor.fetchall()

    # Ambil total deteksi dan total manusia
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_detections,
            COALESCE(SUM(human_count), 0) AS total_humans
        FROM detections
        WHERE device_id = %s
    """, (device_id,))
    totals = cursor.fetchone()

    cursor.close()
    conn.close()

    # Pastikan tidak error saat recent kosong
    latest_count = recent[0]["human_count"] if recent else 0

    return {
        "recent_detections": recent,
        "total_detections": totals.get("total_detections", 0),
        "human_count": latest_count
    }
