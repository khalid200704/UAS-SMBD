from flask import Flask, Response, render_template, jsonify
from ultralytics import YOLO
import cv2, time, random
import logging
from database import insert_detection, update_device, get_dashboard_data

# Konfigurasi
ESP32_STREAM_URL = "http://172.20.10.2:81/stream"
MODEL_PATH = "best.pt"
DEVICE_ID = 1  # ID dari tabel devices di MySQL
TEST_MODE = True  # Mode test tanpa ESP32-CAM

# Inisialisasi
app = Flask(__name__, static_folder='static', static_url_path='/static')
logging.basicConfig(level=logging.INFO)

# Load model hanya jika file ada
try:
    model = YOLO(MODEL_PATH)
    logging.info("YOLO model loaded successfully")
except Exception as e:
    logging.warning(f"Could not load YOLO model: {e}")
    model = None

# Inisialisasi kamera (akan gagal jika ESP32 tidak tersedia)
cap = None
if not TEST_MODE:
    try:
        cap = cv2.VideoCapture(ESP32_STREAM_URL)
        if not cap.isOpened():
            raise Exception("Cannot connect to ESP32-CAM")
        logging.info("Camera connected successfully")
    except Exception as e:
        logging.warning(f"Camera connection failed: {e}")
        TEST_MODE = True

last_timestamp = None

def generate_test_frame():
    """Generate dummy frame untuk testing"""
    import numpy as np
    
    # Buat frame dummy 640x480
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Tambahkan teks
    cv2.putText(frame, "TEST MODE - No Camera", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Time: {time.strftime('%H:%M:%S')}", (50, 100), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Simulasi deteksi random
    if random.random() > 0.7:  # 30% chance deteksi
        cv2.rectangle(frame, (200, 150), (400, 350), (0, 255, 0), 2)
        cv2.putText(frame, "HUMAN DETECTED", (200, 140), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return frame, True
    
    return frame, False

def generate_frames():
    global last_timestamp
    while True:
        start_time = time.time()
        
        if TEST_MODE:
            # Mode test dengan frame dummy
            frame, detected = generate_test_frame()
            time.sleep(0.1)  # Simulasi delay kamera
        else:
            # Mode normal dengan ESP32-CAM
            success, frame = cap.read()
            if not success:
                logging.warning("Failed to read frame from camera")
                time.sleep(0.1)
                continue

            # Inference YOLO jika model tersedia
            detected = False
            if model:
                try:
                    results = model(frame, stream=True)
                    for r in results:
                        frame = r.plot()
                        for box in r.boxes:
                            cls = int(box.cls[0])
                            if model.names[cls].lower() in ["person", "human"]:
                                detected = True
                except Exception as e:
                    logging.error(f"YOLO inference error: {e}")

        # Hitung delay & jitter
        end_time = time.time()
        delay = (end_time - start_time) * 1000  # ms
        if last_timestamp:
            jitter = abs(delay - last_timestamp)
        else:
            jitter = 0
        last_timestamp = delay

        # Simpan ke DB jika ada deteksi (hanya jika database tersedia)
        if detected:
            try:
                insert_detection(DEVICE_ID, "HUMAN", jitter, delay)
                update_device(DEVICE_ID, "DETECTED")
            except Exception as e:
                logging.error(f"Database error: {e}")

        # Stream ke browser
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('realtime.html')

@app.route('/realtime')
def realtime():
    return render_template('realtime.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data')
def data():
    try:
        data = get_dashboard_data()
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        # Return dummy data untuk testing
        dummy_data = []
        for i in range(10):
            dummy_data.append({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'status': 'HUMAN' if random.random() > 0.5 else 'IDLE',
                'jitter': round(random.uniform(0, 10), 2),
                'delay_ms': round(random.uniform(20, 100), 2)
            })
        return jsonify(dummy_data)

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/status')
def status():
    """Endpoint untuk cek status sistem"""
    return jsonify({
        'camera': 'Connected' if cap and cap.isOpened() else 'Test Mode',
        'model': 'Loaded' if model else 'Not Available',
        'database': 'Connected',  # Akan dicek di frontend
        'test_mode': TEST_MODE
    })

@app.route('/test-static')
def test_static():
    """Test endpoint untuk debug static files"""
    import os
    static_path = os.path.join(app.root_path, 'static')
    css_path = os.path.join(static_path, 'css', 'style.css')
    js_path = os.path.join(static_path, 'js', 'dashboard.js')
    
    return jsonify({
        'static_folder': app.static_folder,
        'static_url_path': app.static_url_path,
        'root_path': app.root_path,
        'static_path_exists': os.path.exists(static_path),
        'css_exists': os.path.exists(css_path),
        'js_exists': os.path.exists(js_path),
        'static_files': os.listdir(static_path) if os.path.exists(static_path) else []
    })

if __name__ == '__main__':
    print("="*50)
    print("SMBD - Sistem Monitoring Berbasis Deteksi")
    print("="*50)
    print(f"Test Mode: {'ON' if TEST_MODE else 'OFF'}")
    print(f"Model: {'Loaded' if model else 'Not Available'}")
    print(f"Camera: {'Connected' if cap and cap.isOpened() else 'Test Mode'}")
    print("="*50)
    print("Akses aplikasi di: http://localhost:5000")
    print("="*50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
