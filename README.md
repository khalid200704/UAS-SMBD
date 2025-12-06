# SMBD - Sistem Monitoring Berbasis Deteksi

Sistem pemantauan real-time berbasis edge computing yang menggunakan Flask, YOLOv8, dan MySQL untuk deteksi manusia melalui ESP32-CAM.

## 🚀 Fitur Utama

- **Real-time Video Streaming**: Video langsung dari ESP32-CAM atau Webcam
- **Deteksi Manusia**: Menggunakan model YOLOv8 yang telah dilatih
- **Edge Computing**: Pemrosesan dilakukan di laptop, bukan cloud
- **Performance Monitoring**: Tracking delay dan jitter real-time
- **Dashboard Interaktif**: Visualisasi data
- **Database Logging**: Penyimpanan data deteksi ke MySQL

## 🛠️ Teknologi yang Digunakan

- **Backend**: Flask (Python)
- **AI/ML**: YOLOv8 (Ultralytics)
- **Computer Vision**: OpenCV
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Hardware**: ESP32-CAM

## 📋 Prasyarat

- Python 3.8+
- MySQL Server
- ESP32-CAM dengan streaming capability (opsional jika tidak pakai webcam)
- Model YOLOv8 terlatih (`best.pt`)
- (Windows) Izin kamera aktif untuk aplikasi desktop

## 🔧 Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/khalid200704/UAS-SMBD.git
cd SMBD
```

### 2. Install Dependencies

Untuk Python 3.13+ (disarankan):
```bash
pip install -r requirements_minimal.txt
```

Untuk Python 3.8–3.11:
```bash
pip install -r requirements.txt
```

Manual jika perlu:
```bash
pip install Flask opencv-python ultralytics mysql-connector-python python-dotenv
```

### 3. Setup Database
1. Jalankan MySQL
2. Import schema database:
```sql
source database_schema.sql
```

### 4. Konfigurasi
1. Salin `.env.example` menjadi `.env`
2. Edit `.env` untuk menyesuaikan konfigurasi (DB, sumber video, model, dsb.)

Contoh `.env` lengkap:
```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=yolo_edge

# Device
DEVICE_ID=1

# Model
MODEL_PATH=best.pt

# Video Source (pilih salah satu)
# Webcam mode
USE_WEBCAM=false
WEBCAM_INDEX=0

# ESP32-CAM mode (pakai jika USE_WEBCAM=false)
ESP32_STREAM_URL=http://192.168.4.1/stream

# App Settings
SKIP_RATE=5
MAX_FPS=10
```

### 5. Jalankan Aplikasi

```bash
python app.py
```

Aplikasi berjalan di `http://localhost:5000`

Endpoint penting:
- `/` dashboard/login
- `/realtime` halaman realtime
- `/video_feed` stream MJPEG
- `/data` ringkasan statistik
- `/health` status kamera/database/model

## 📱 Cara Penggunaan

### Dashboard Utama
1. Akses `http://localhost:5000`
2. Lihat status sistem (Camera, Database, Model)
3. Mulai monitoring

### Real-time Monitoring
- Video stream langsung dari kamera
- Ringkasan statistik deteksi

## 🗂️ Struktur Project (ringkas)
```
SMBD/
├── app.py                    # Aplikasi Flask utama
├── database.py              # Koneksi dan operasi database
├── database_schema.sql      # Schema database MySQL
├── best.pt                  # Model YOLOv8 terlatih
├── requirements.txt         # Dependencies Python
├── requirements_minimal.txt # Dependencies minimal (Python 3.13+)
├── camera_capture.py        # Utilitas buka/reconnect capture & baca frame
├── test_camera.py           # Skrip uji koneksi stream/menyimpan frame
├── .env.example            # Template konfigurasi environment
├── README.md               # Dokumentasi
├── templates/             # Template HTML
│   └── simple.html        # Halaman monitoring sederhana
└── static/               # Asset statis
    ├── css/
    │   └── simple.css    # Styling CSS minimal
    └── js/
        └── simple.js     # JavaScript real-time
```

## 🔄 Alur Kerja Sistem
1. ESP32-CAM mengirim stream video via HTTP
2. Laptop menerima dan memproses setiap frame
3. YOLOv8 mendeteksi manusia dalam frame
4. Sistem menghitung delay dan jitter
5. Data deteksi disimpan ke MySQL
6. Browser menampilkan video dan grafik/statistik

## 📊 Database Schema (ringkas)
- `users`: login (password hash bcrypt)
- `devices`: info perangkat, total deteksi, status terakhir
- `detections`: log deteksi (timestamp, status, jitter, delay, human_count)

## 🚨 Troubleshooting
- **Paket gagal terpasang (Python terbaru)**: gunakan `requirements_minimal.txt`
- **Kamera tidak terhubung (ESP32)**:
  - Buka `http://<IP-ESP32>:81/` di browser, pastikan streaming aktif
  - Cek firewall/antivirus yang memblokir port 81
  - Turunkan resolusi/FPS di firmware ESP32 jika perlu
- **Webcam tidak terbaca (Windows)**:
  - Pastikan aplikasi lain (Teams/Zoom/OBS/Camera) tidak memakai webcam
  - Ubah `WEBCAM_INDEX` ke 0/1/2 sesuai perangkat
  - Aktifkan Settings → Privacy & security → Camera → Allow desktop apps
  - Aplikasi memakai backend `CAP_DSHOW` untuk stabilitas
- **WARNING: Failed to read frame from camera**:
  - Coba mode lain: set `USE_WEBCAM=true` untuk uji webcam, atau `false` untuk uji ESP32
  - Ganti `WEBCAM_INDEX` dan restart aplikasi
  - Cek `/health` → `camera: connected` menandakan capture terbuka
  - Jalankan uji: `python test_camera.py` (menyimpan `test_frame.jpg` jika sukses)
- **Database error**: pastikan MySQL berjalan, kredensial `.env` benar, dan schema terimport
- **Model tidak ditemukan**: pastikan `best.pt` ada di root atau set `MODEL_PATH` yang benar

## 📈 Tips Performance
- Gunakan GPU (CUDA) bila tersedia
- Turunkan resolusi ESP32-CAM
- Gunakan model YOLOv8 yang lebih kecil

## 📄 Lisensi
MIT (sesuaikan sesuai kebutuhan)
