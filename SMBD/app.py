from flask import Flask, Response, render_template, jsonify
from ultralytics import YOLO
import cv2, time
import logging
from database import insert_detection, update_device, get_dashboard_data

# Konfigurasi
ESP32_STREAM_URL = "http://172.20.10.2:81/stream"
MODEL_PATH = "best.pt"
DEVICE_ID = 1  # ID dari tabel devices di MySQL

# Inisialisasi
app = Flask(__name__)
# Set logging level to INFO
logging.basicConfig(level=logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.INFO)
model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(ESP32_STREAM_URL)

last_timestamp = None

# Batasi deteksi hanya pada kelas person/human jika tersedia
try:
    # Strip whitespace dan case-insensitive match
    PERSON_CLASS_IDS = [i for i, n in model.names.items() if str(n).strip().lower() in ["person", "human"]]
    logging.info(f"Model classes: {model.names}")
    logging.info(f"Person class IDs: {PERSON_CLASS_IDS}")
except Exception as e:
    logging.warning(f"Error getting class IDs: {e}")
    PERSON_CLASS_IDS = []

def generate_frames():
    global last_timestamp
    while True:
        start_time = time.time()
        success, frame = cap.read()
        if not success:
            logging.warning("Failed to read frame from camera")
            time.sleep(0.1)
            continue

        # Inference YOLO
        # Deteksi semua kelas Human (index 0 dan 1)
        results = model(
            frame,
            stream=True,
            conf=0.3,   # confidence threshold (turunkan ke 0.3 untuk lebih sensitif)
            iou=0.45,   # NMS IoU threshold
            max_det=5,  # batasi jumlah box per frame
            classes=PERSON_CLASS_IDS if PERSON_CLASS_IDS else None
        )
        detected = False
        annotated = frame

        for r in results:
            annotated = r.plot()
            # Jika ada box apapun yang terdeteksi, set detected = True
            if len(r.boxes) > 0:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    class_name = model.names[cls].strip().lower()
                    # Cek apakah kelas adalah person/human (case-insensitive, strip whitespace)
                    if class_name in ["person", "human"] or not PERSON_CLASS_IDS:
                        detected = True
                        break

        # Hitung delay & jitter
        end_time = time.time()
        delay = (end_time - start_time) * 1000  # ms
        if last_timestamp:
            jitter = abs(delay - last_timestamp)
        else:
            jitter = 0
        last_timestamp = delay

        # Hitung jumlah orang yang terdeteksi
        human_count = 0
        if detected:
            for r in results:
                if hasattr(r, 'boxes') and r.boxes is not None:
                    human_count = len([box for box in r.boxes 
                                    if int(box.cls[0]) in PERSON_CLASS_IDS or not PERSON_CLASS_IDS])
        
        # Simpan ke DB jika ada deteksi
        if detected:
            try:
                insert_detection(DEVICE_ID, "HUMAN", jitter, delay, human_count)
                update_device(DEVICE_ID, "DETECTED")
                logging.info(f"Human detected at device {DEVICE_ID}, count={human_count}, delay={delay:.1f}ms, jitter={jitter:.1f}ms")
            except Exception as e:
                logging.error(f"Database error: {e}")
        # Stream ke browser
        _, buffer = cv2.imencode('.jpg', annotated)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('simple.html')

@app.route('/realtime')
def realtime():
    return render_template('realtime.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/data')
def data():
    try:
        data = get_dashboard_data(DEVICE_ID)
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return jsonify({'recent_detections': [], 'total_detections': 0}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

@app.route('/health')
def health():
    """Endpoint untuk cek status sistem"""
    try:
        # Cek kamera
        camera_ok = cap.isOpened()
        
        # Cek database
        from database import get_connection
        db_ok = False
        try:
            conn = get_connection()
            if conn.is_connected():
                db_ok = True
                conn.close()
        except Exception as db_error:
            logging.error(f"Database connection error: {db_error}")
            db_ok = False
            
        return jsonify({
            'status': 'OK',
            'camera': 'connected' if camera_ok else 'disconnected',
            'database': 'connected' if db_ok else 'disconnected'
        })
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return jsonify({
            'status': 'ERROR',
            'error': str(e)
        }), 500
