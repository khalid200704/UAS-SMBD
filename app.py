from flask import Flask, Response, render_template, jsonify, request, session, redirect, url_for, make_response
from flask import session as flask_session
from ultralytics import YOLO
import cv2, time, logging
from database import insert_detection, update_device, get_dashboard_data
import bcrypt
from flask_cors import CORS

# ==========================
# Konfigurasi
# ==========================
ESP32_STREAM_URL = "http://172.20.10.2:81/stream"
MODEL_PATH = "best.pt"
DEVICE_ID = 1
SKIP_RATE = 5
MAX_FPS = 10

last_delay = None      # untuk delay/jitter
last_db_insert = 0     # untuk rate limit DB insert

# ==========================
# Inisialisasi
# ==========================
app = Flask(__name__)
app.config.update(
    SECRET_KEY='gantiKeRandomKeyRahasia',  # Jangan lupa ganti di production
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

# Configure CORS with credentials support
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5000", "http://172.20.10.5:5000", "http://localhost"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

logging.basicConfig(level=logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.INFO)

model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(ESP32_STREAM_URL)
last_timestamp = None

# ==========================
# Deteksi hanya kelas "person" / "human"
# ==========================
try:
    PERSON_CLASS_IDS = [i for i, n in model.names.items() if str(n).strip().lower() in ["person", "human"]]
    logging.info(f"Model classes: {model.names}")
    logging.info(f"Person class IDs: {PERSON_CLASS_IDS}")
except Exception as e:
    logging.warning(f"Error getting class IDs: {e}")
    PERSON_CLASS_IDS = []

# ==========================
# Stream kamera + deteksi YOLO
# ==========================
# Tambahkan variabel global di awal
last_db_insert = 0   # Waktu deteksi terakhir yang dicatat DB (dalam detik/epoch)

def generate_frames():
    global last_delay, last_db_insert
    frame_id = 0
    prev_time = time.time()

    while True:
        success, frame = cap.read()
        if not success:
            logging.warning("Failed to read frame from camera")
            time.sleep(0.1)
            continue

        detected = False
        human_count = 0
        annotated = frame

        if frame_id % SKIP_RATE == 0:
            start_time = time.time()
            results = model(
                frame,
                conf=0.2,
                iou=0.45,
                max_det=5,
                classes=PERSON_CLASS_IDS if PERSON_CLASS_IDS else None
            )

            annotated = results[0].plot()
            for r in results:
                if len(r.boxes) > 0:
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        class_name = model.names[cls].strip().lower()
                        if class_name in ["person", "human"] or not PERSON_CLASS_IDS:
                            detected = True
                    human_count += len([
                        box for box in r.boxes if int(box.cls[0]) in PERSON_CLASS_IDS or not PERSON_CLASS_IDS
                    ])

            # Delay & jitter untuk deteksi saja
            end_time = time.time()
            delay = (end_time - start_time) * 1000
            jitter = abs(delay - last_delay) if last_delay else 0
            last_delay = delay

            # Rate-limit ke database: jika deteksi, hanya insert jika sudah lewat 60 detik
            current_time = time.time()
            if detected and (current_time - last_db_insert) > 60:
                try:
                    insert_detection(DEVICE_ID, "HUMAN", jitter, delay, human_count)
                    update_device(DEVICE_ID, "DETECTED")
                    logging.info(f"Human detected at device {DEVICE_ID}, count={human_count}, delay={delay:.1f}ms, jitter={jitter:.1f}ms [DB INSERT]")
                    last_db_insert = current_time
                except Exception as e:
                    logging.error(f"Database error: {e}")
            elif detected:
                logging.info(f"Human detected, skipping DB insert (interval < 1 menit)")

        # Batasi FPS ke browser
        t_now = time.time()
        elapsed = t_now - prev_time
        if elapsed < 1.0 / MAX_FPS:
            time.sleep((1.0 / MAX_FPS) - elapsed)
        prev_time = time.time()

        # Encode + stream
        _, buffer = cv2.imencode('.jpg', annotated)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        frame_id += 1

# ==========================
# ROUTES
# ==========================
@app.route('/')
def index():
    print("\n=== Accessing root route ===")
    print(f"Session data: {dict(session)}")
    print(f"Request headers: {dict(request.headers)}")
    
    # Check if user is logged in
    if 'username' not in session:
        print("User not in session, redirecting to login")
        # Add cache control headers to prevent caching of the redirect
        response = make_response(redirect(url_for('login')))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    print(f"User {session.get('username')} is logged in")
    
    # Return the main template for logged-in users
    response = make_response(render_template('simple.html'))
    
    # Set CORS headers
    origin = request.headers.get('Origin', '*')
    print(f"Setting CORS headers for origin: {origin}")
    
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, *'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    response.headers['Vary'] = 'Origin'
    
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    print("Serving main page")
    return response

@app.route('/login')
def login():
    return render_template('login.html')

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
        payload = {
            "human_count": data.get("human_count", data.get("total_humans", 0)),
            "total_detections": data.get("total_detections", 0),
            "recent_detections": data.get("recent_detections", [])
        }

        return jsonify(payload)

    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return jsonify({
            "human_count": 0,
            "total_detections": 0,
            "recent_detections": []
        }), 500

@app.route('/health')
def health():
    """Endpoint untuk cek status sistem"""
    try:
        camera_ok = cap.isOpened()

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

        model_ok = False
        try:
            if model is not None:
                model_ok = True
        except Exception:
            model_ok = False

        return jsonify({
            'status': 'OK',
            'camera': 'connected' if camera_ok else 'disconnected',
            'database': 'connected' if db_ok else 'disconnected',
            'model': 'loaded' if model_ok else 'not_loaded'
        })
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return jsonify({
            'status': 'ERROR',
            'error': str(e)
        }), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def api_login():
    print("\n=== Login Attempt ===")
    print(f"Method: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    
    if request.method == 'OPTIONS':
        print("Handling OPTIONS preflight request")
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        return response
        
    try:
        data = request.get_json()
        print(f"Received login data: {data}")
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            print("Error: Missing username or password")
            return jsonify({'success': False, 'message': 'Data tidak lengkap'}), 400

        from database import get_connection
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        
        print(f"Querying database for user: {username}")
        cur.execute('SELECT * FROM users WHERE username=%s', (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            print(f"User not found: {username}")
            return jsonify({'success': False, 'message': 'Username tidak ditemukan!'}), 401
            
        print(f"Found user: {user['username']} (ID: {user['id']})")

        # Check password with bcrypt
        try:
            stored_password = user['password']
            print(f"Stored password (first 10 chars): {str(stored_password)[:10]}...")
            
            # Ensure stored_password is a string
            if not isinstance(stored_password, (str, bytes)):
                stored_password = str(stored_password)
            
            # Check if the stored password is already hashed with bcrypt
            if stored_password.startswith('$2b$'):
                print("Password appears to be hashed with bcrypt")
                
                # Verify the hashed password
                password_matches = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
                print(f"Password matches: {password_matches}")
                
                if password_matches:
                    # Clear any existing session
                    session.clear()
                    print("Cleared existing session")
                    
                    # Set new session data
                    session['username'] = user['username']
                    session['role'] = user['role']
                    session.permanent = True  # Make the session persistent
                    print(f"Set session data - username: {user['username']}, role: {user['role']}")
                    
                    # Create response
                    response_data = {
                        'success': True, 
                        'message': 'Login berhasil',
                        'redirect': '/',
                        'user': {
                            'username': user['username'],
                            'role': user['role']
                        }
                    }
                    print(f"Response data: {response_data}")
                    
                    response = jsonify(response_data)
                    
                    # Set CORS headers
                    origin = request.headers.get('Origin', '*')
                    print(f"Setting CORS headers for origin: {origin}")
                    
                    response.headers.add('Access-Control-Allow-Credentials', 'true')
                    response.headers.add('Access-Control-Allow-Origin', origin)
                    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
                    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                    
                    print("Sending successful login response")
                    return response
                
                return jsonify({
                    'success': False, 
                    'message': 'Password salah!'
                }), 401
            else:
                # If password is not hashed, log a warning and don't allow login
                logging.warning(f'User {username} has unhashed password. Please run hash_passwords.py')
                return jsonify({
                    'success': False, 
                    'message': 'Password tidak aman. Silakan hubungi administrator.'
                }), 401
                
        except Exception as pwd_error:
            logging.error(f'Password check error: {pwd_error}', exc_info=True)
            return jsonify({
                'success': False, 
                'message': 'Terjadi kesalahan saat memverifikasi password'
            }), 500
            
    except Exception as e:
        logging.error(f'Login error: {e}', exc_info=True)
        return jsonify({
            'success': False, 
            'message': f'Error: {str(e)}'
        }), 500

# ==========================
# RUN SERVER
# ==========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
