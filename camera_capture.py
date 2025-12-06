"""
Script untuk mengambil gambar dari ESP32-CAM atau webcam setiap interval
"""

import cv2
import os
from datetime import datetime
import time
import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi
ESP32_STREAM_URL = os.getenv("ESP32_STREAM_URL")
CAPTURE_INTERVAL = int(os.getenv("CAPTURE_INTERVAL", "30"))  # detik
OUTPUT_DIR = os.getenv("CAPTURE_OUTPUT_DIR", "captures")
USE_WEBCAM = os.getenv("USE_WEBCAM", "false").lower() == "true"
WEBCAM_INDEX = int(os.getenv("WEBCAM_INDEX", "0"))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_output_directory():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logger.info(f"Folder '{OUTPUT_DIR}' created")

def open_capture():
    if USE_WEBCAM:
        logger.info(f"Opening webcam index {WEBCAM_INDEX}...")
        # On Windows, CAP_DSHOW is often more reliable
        try:
            if os.name == 'nt':
                cap = cv2.VideoCapture(WEBCAM_INDEX, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(WEBCAM_INDEX)
        except Exception:
            cap = cv2.VideoCapture(WEBCAM_INDEX)
    else:
        logger.info(f"Connecting to camera at {ESP32_STREAM_URL}...")
        # Prefer FFMPEG backend for network streams when available
        try:
            cap = cv2.VideoCapture(ESP32_STREAM_URL, cv2.CAP_FFMPEG)
        except Exception:
            cap = cv2.VideoCapture(ESP32_STREAM_URL)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap

def capture_frame(cap):
    try:
        for _ in range(3):
            success, frame = cap.read()
            if success and frame is not None:
                return frame
            time.sleep(0.5)
        logger.warning("Failed to read frame from camera after 3 attempts")
        return None
    except Exception as e:
        logger.error(f"Error capturing frame: {e}")
        return None

def reconnect_camera(old_cap):
    logger.info("Attempting to reconnect to camera...")
    try:
        if old_cap is not None:
            old_cap.release()
        time.sleep(1)
    except Exception:
        pass
    new_cap = open_capture()
    if new_cap.isOpened():
        logger.info("Camera reconnected successfully!")
        return new_cap
    else:
        logger.error("Failed to reconnect to camera!")
        return None

def save_frame(frame, filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    cv2.imwrite(filepath, frame)
    logger.info(f"Frame saved: {filepath}")

def main():
    create_output_directory()
    cap = open_capture()

    if not cap.isOpened():
        logger.error("Cannot connect to camera! Check device/URL and network.")
        return

    logger.info("Camera connected successfully!")
    logger.info(f"Starting capture every {CAPTURE_INTERVAL} seconds...")
    logger.info(f"Saving images to: {os.path.abspath(OUTPUT_DIR)}")
    logger.info("Press Ctrl+C to stop")

    frame_count = 0
    failed_attempts = 0
    max_failed_attempts = 3

    try:
        while True:
            frame = capture_frame(cap)
            if frame is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}_{frame_count:04d}.png"
                save_frame(frame, filename)
                frame_count += 1
                failed_attempts = 0
                logger.info(f"Total captures: {frame_count}")
                logger.info(f"Waiting {CAPTURE_INTERVAL} seconds until next capture...")
                time.sleep(CAPTURE_INTERVAL)
            else:
                failed_attempts += 1
                logger.warning(f"Failed to capture frame ({failed_attempts}/{max_failed_attempts})")
                if failed_attempts >= max_failed_attempts:
                    cap = reconnect_camera(cap)
                    if cap is None:
                        logger.error("Failed to reconnect! Waiting 5 seconds before retry...")
                        time.sleep(5)
                    failed_attempts = 0
                else:
                    time.sleep(0.5)
    except KeyboardInterrupt:
        logger.info("\nStopping capture...")
        logger.info(f"Total images captured: {frame_count}")
    finally:
        try:
            cap.release()
        except Exception:
            pass
        logger.info("Camera released. Goodbye!")

if __name__ == "__main__":
    main()
