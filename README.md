# SMBD - Sistem Monitoring Berbasis Deteksi

Sistem pemantauan real-time berbasis edge computing yang menggunakan Flask, YOLOv8, dan MySQL untuk deteksi manusia melalui ESP32-CAM.

## 🚀 Fitur Utama

- **Real-time Video Streaming**: Video langsung dari ESP32-CAM
- **Deteksi Manusia**: Menggunakan model YOLOv8 yang telah dilatih
- **Edge Computing**: Pemrosesan dilakukan di laptop, bukan cloud
- **Performance Monitoring**: Tracking delay dan jitter real-time
- **Dashboard Interaktif**: Visualisasi data menggunakan Chart.js
- **Database Logging**: Penyimpanan data deteksi ke MySQL

## 🛠️ Teknologi yang Digunakan

- **Backend**: Flask (Python)
- **AI/ML**: YOLOv8 (Ultralytics)
- **Computer Vision**: OpenCV
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **Hardware**: ESP32-CAM

## 📋 Prasyarat

- Python 3.8+
- MySQL Server
- XAMPP (untuk MySQL dan web server)
- ESP32-CAM dengan streaming capability
- Model YOLOv8 terlatih (`best.pt`)

## 🔧 Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd SMBD
```

### 2. Install Dependencies

**Untuk Python 3.13+ (Recommended):**
```bash
pip install -r requirements_minimal.txt
```

**Untuk Python 3.8-3.11:**
```bash
pip install -r requirements.txt
```

**Manual installation jika ada masalah:**
```bash
pip install Flask opencv-python ultralytics mysql-connector-python python-dotenv
```

### 3. Setup Database
1. Jalankan XAMPP dan start MySQL
2. Buka phpMyAdmin atau MySQL command line
3. Import schema database:
```sql
source database_schema.sql
```

### 4. Konfigurasi
1. Pastikan ESP32-CAM streaming di `http://172.20.10.2:81/stream`
2. Sesuaikan konfigurasi database di `database.py` jika diperlukan
3. Pastikan file `best.pt` (model YOLOv8) ada di root directory

### 5. Jalankan Aplikasi

**Mode Test (tanpa ESP32-CAM):**
```bash
python app_test.py
```
atau double-click `run_app.bat`

**Mode Production (dengan ESP32-CAM):**
```bash
python app.py
```

Aplikasi akan berjalan di `http://localhost:5000`

**Mode Test Features:**
- Simulasi video stream dengan frame dummy
- Random human detection untuk testing
- Dummy data jika database tidak tersedia
- Tidak memerlukan ESP32-CAM atau model YOLO

## 📱 Cara Penggunaan

### Dashboard Utama
1. Buka browser dan akses `http://localhost:5000`
2. Lihat status sistem (Camera, Database, Model)
3. Klik tombol "Mulai Monitoring" untuk memulai

### Real-time Monitoring
1. Halaman akan menampilkan video stream langsung
2. Grafik real-time menunjukkan:
   - Jumlah deteksi manusia
   - Delay pemrosesan
   - Jitter (variasi delay)
3. Tabel menampilkan log deteksi terbaru
4. Stats cards menunjukkan ringkasan performa

## 🗂️ Struktur Project

```
SMBD/
├── app.py                    # Aplikasi Flask utama
├── app_test.py              # Mode test tanpa ESP32-CAM
├── database.py              # Koneksi dan operasi database
├── database_schema.sql      # Schema database MySQL
├── migration_cleanup.sql    # SQL cleanup untuk kolom tidak terpakai
├── best.pt                  # Model YOLOv8 terlatih
├── requirements.txt         # Dependencies Python
├── requirements_minimal.txt # Dependencies minimal (Python 3.13+)
├── .env.example            # Template konfigurasi environment
├── README.md               # Dokumentasi
├── run_app.bat            # Batch file untuk Windows
├── templates/             # Template HTML
│   └── simple.html        # Halaman monitoring sederhana
└── static/               # Asset statis
    ├── css/
    │   └── simple.css    # Styling CSS minimal
    └── js/
        └── simple.js     # JavaScript real-time
```

## 🔄 Alur Kerja Sistem

1. **Video Capture**: ESP32-CAM mengirim stream video via HTTP
2. **Frame Processing**: Laptop menerima dan memproses setiap frame
3. **YOLO Inference**: Model YOLOv8 mendeteksi manusia dalam frame
4. **Performance Metrics**: Sistem menghitung delay dan jitter
5. **Database Logging**: Data deteksi disimpan ke MySQL
6. **Real-time Display**: Browser menampilkan video dan grafik real-time

## 📊 Database Schema

### Tabel `devices`
- `id`: Primary key
- `device_name`: Nama perangkat
- `ip_address`: IP address ESP32-CAM
- `total_human_detection`: Total deteksi
- `last_status`: Status terakhir
- `last_active`: Waktu aktif terakhir

### Tabel `detections`
- `id`: Primary key
- `device_id`: Foreign key ke devices
- `timestamp`: Waktu deteksi
- `status`: Status deteksi (HUMAN/IDLE)
- `jitter`: Nilai jitter (ms)
- `delay_ms`: Nilai delay (ms)

## ⚙️ Konfigurasi

### ESP32-CAM Setup
Pastikan ESP32-CAM dikonfigurasi untuk streaming video di:
```
http://172.20.10.2:81/stream
```

### Database Configuration
1. Copy `.env.example` menjadi `.env`
2. Edit `.env` untuk menyesuaikan konfigurasi:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=yolo_edge
ESP32_STREAM_URL=http://172.20.10.2:81/stream
DEVICE_ID=1
```

### API Endpoints
- `GET /` - Halaman monitoring utama
- `GET /video_feed` - Stream video real-time
- `GET /data` - Data deteksi dan statistik (JSON)
- `GET /health` - Status sistem (camera, database, model)

## 🚨 Troubleshooting

### Masalah Umum

1. **Package installation error (Python 3.13+)**
   - Gunakan `requirements_minimal.txt` untuk Python versi terbaru
   - Atau install manual: `pip install Flask opencv-python ultralytics mysql-connector-python python-dotenv`

2. **Camera tidak terhubung**
   - Periksa IP address ESP32-CAM
   - Pastikan ESP32-CAM dalam jaringan yang sama

3. **Database error**
   - Pastikan MySQL service berjalan
   - Periksa kredensial database
   - Jalankan schema SQL

4. **Model tidak ditemukan**
   - Pastikan file `best.pt` ada di root directory
   - Periksa path model di `app.py`

5. **Performance lambat**
   - Kurangi resolusi video ESP32-CAM
   - Gunakan model YOLOv8 yang lebih kecil (YOLOv8n)

## 📈 Optimisasi Performance

- Gunakan GPU untuk inference (CUDA)
- Sesuaikan FPS streaming ESP32-CAM
- Implementasi frame skipping jika diperlukan
- Optimasi ukuran model YOLOv8

## 🤝 Kontribusi

1. Fork repository
2. Buat branch fitur (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📄 Lisensi

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Kontak

Project Link: [https://github.com/username/SMBD](https://github.com/username/SMBD)
