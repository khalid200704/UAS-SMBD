"""
Script untuk mengambil gambar dari ESP32-CAM setiap 1 menit
dan menyimpannya ke folder "captures" di laptop
"""

import cv2
import os
from datetime import datetime
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi
ESP32_STREAM_URL = "http://172.20.10.2:81/stream"
CAPTURE_INTERVAL = 30  # 1 menit (60 detik)
OUTPUT_DIR = "captures"

def create_output_directory():
    """Buat folder untuk menyimpan gambar jika belum ada"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info(f"Folder '{OUTPUT_DIR}' created")

def capture_frame(cap):
    """Ambil satu frame dari kamera dengan error handling"""
    try:
        # Coba baca frame maksimal 3 kali
        for attempt in range(3):
            success, frame = cap.read()
            if success and frame is not None:
                return frame
            time.sleep(0.5)  # Tunggu sebentar sebelum retry
        logger.warning("Failed to read frame from camera after 3 attempts")
        return None
    except Exception as e:
        logger.error(f"Error capturing frame: {e}")
        return None

def reconnect_camera(old_cap):
    """Reconnect ke kamera jika terputus"""
    logger.info("Attempting to reconnect to camera...")
    try:
        if old_cap is not None:
            old_cap.release()
        time.sleep(1)  # Tunggu sebentar sebelum reconnect
    except:
        pass
    
    new_cap = cv2.VideoCapture(ESP32_STREAM_URL)
    # Set buffer size agar tidak crash
    new_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if new_cap.isOpened():
        logger.info("Camera reconnected successfully!")
        return new_cap
    else:
        logger.error("Failed to reconnect to camera!")
        return None

def save_frame(frame, filename):
    """Simpan frame ke file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    cv2.imwrite(filepath, frame)
    logger.info(f"Frame saved: {filepath}")

def main():
    """Fungsi utama untuk capture gambar setiap interval"""
    
    # Buat folder output
    create_output_directory()
    
    # Koneksi ke ESP32-CAM dengan timeout
    logger.info(f"Connecting to camera at {ESP32_STREAM_URL}...")
    cap = cv2.VideoCapture(ESP32_STREAM_URL)
    
    # Set buffer size agar tidak crash
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    
    if not cap.isOpened():
        logger.error("Cannot connect to camera! Please check:")
        logger.error("1. ESP32-CAM is powered on")
        logger.error("2. ESP32-CAM is on the same network")
        logger.error("3. Stream URL is correct")
        return
    
    logger.info("Camera connected successfully!")
    logger.info(f"Starting capture every {CAPTURE_INTERVAL} seconds...")
    logger.info(f"Saving images to: {os.path.abspath(OUTPUT_DIR)}")
    logger.info("Press Ctrl+C to stop")
    
    frame_count = 0
    failed_attempts = 0
    max_failed_attempts = 3  # Maksimal gagal coba sebelum reconnect
    
    try:
        while True:
            # Baca frame dari kamera
            frame = capture_frame(cap)
            
            if frame is not None:
                # Generate filename dengan timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}_{frame_count:04d}.png"
                
                # Simpan frame
                save_frame(frame, filename)
                frame_count += 1
                failed_attempts = 0  # Reset counter jika berhasil
                
                logger.info(f"Total captures: {frame_count}")
                
                # TUNGGU 30 DETIK hanya jika berhasil capture
                logger.info(f"Waiting {CAPTURE_INTERVAL} seconds until next capture...")
                time.sleep(CAPTURE_INTERVAL)
                
            else:
                failed_attempts += 1
                logger.warning(f"Failed to capture frame ({failed_attempts}/{max_failed_attempts})")
                
                # Jika terlalu banyak gagal, reconnect
                if failed_attempts >= max_failed_attempts:
                    logger.info("Too many failed attempts, reconnecting camera...")
                    cap = reconnect_camera(cap)
                    if cap is None:
                        logger.error("Failed to reconnect! Waiting 5 seconds before retry...")
                        time.sleep(5)
                    failed_attempts = 0
                else:
                    # Jika belum terlalu banyak gagal, COBA LAGI SEGERA tanpa tunggu
                    logger.info("Retrying immediately...")
                    time.sleep(0.5)  # Delay kecil sebelum retry
            
    except KeyboardInterrupt:
        logger.info("\nStopping capture...")
        logger.info(f"Total images captured: {frame_count}")
    finally:
        cap.release()
        logger.info("Camera released. Goodbye!")

if __name__ == "__main__":
    main()
