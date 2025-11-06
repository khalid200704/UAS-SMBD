# Changelog - SMBD Project Cleanup

## [2025-10-13] - Major Refactoring

### ✅ Perbaikan Backend

#### app.py
- **Ditambahkan**: Endpoint `/health` untuk status sistem real-time (camera, database, model)
- **Diperbaiki**: Error handling di endpoint `/data` sekarang return object konsisten `{recent_detections: [], total_detections: 0}`
- **Ditambahkan**: Logging info saat deteksi manusia berhasil
- **Ditingkatkan**: Filter deteksi hanya kelas person/human dengan `conf=0.6`, `iou=0.5`, `max_det=3`

#### database.py
- **Konsisten**: Query SELECT menggunakan `delay_ms AS delay` untuk frontend
- **Konsisten**: INSERT menggunakan kolom `delay_ms` (bukan `delay`)
- **Diperbaiki**: `get_dashboard_data()` menerima parameter `device_id` (tidak hardcode)

#### database_schema.sql
- **Dibersihkan**: Hapus kolom `human_count` dan `confidence` yang tidak terpakai
- **Konsisten**: Schema sekarang hanya kolom yang digunakan

### ✅ Perbaikan Frontend

#### templates/simple.html
- **Baru**: UI sederhana dan clean dengan UX yang baik
- **Diperbaiki**: Footer tahun tidak pakai Jinja2 syntax yang salah

#### static/js/simple.js
- **Ditambahkan**: Fetch `/health` untuk status badge real-time
- **Diperbaiki**: Update status tiap 5 detik
- **Konsisten**: Gunakan `data.total_detections` dari server (bukan hitung lokal)

#### static/css/simple.css
- **Baru**: Stylesheet minimalis dengan dark theme, responsif, kontras baik

### 🗑️ File Dihapus (Cleanup)

- `templates/realtime.html` - Tidak terpakai (diganti simple.html)
- `static/js/realtime.js` - Tidak terpakai (diganti simple.js)
- `static/css/style.css` - Tidak terpakai (diganti simple.css)

### 📄 File Baru

- `.env.example` - Template konfigurasi environment variables
- `migration_cleanup.sql` - SQL untuk cleanup kolom database tidak terpakai
- `CHANGELOG.md` - File ini

### 📝 Dokumentasi

- **README.md**: Update struktur project, endpoint API, konfigurasi .env

### 🔧 Yang Perlu Dilakukan User

1. **Jalankan migration** (opsional, untuk cleanup database):
   ```sql
   source migration_cleanup.sql
   ```

2. **Buat file .env** (opsional, untuk konfigurasi):
   ```bash
   copy .env.example .env
   # Edit .env sesuai kebutuhan
   ```

3. **Restart server**:
   ```bash
   python app.py
   ```

4. **Test endpoint baru**:
   - `http://localhost:5000/health` - Cek status sistem

### 🎯 Hasil Akhir

- ✅ Backend-frontend konsisten
- ✅ Error handling proper
- ✅ Status sistem real-time
- ✅ UI sederhana dan UX bagus
- ✅ Workspace bersih (file lama dihapus)
- ✅ Dokumentasi lengkap
- ✅ Logging informatif
- ✅ Schema database konsisten

### 📊 Metrik Perubahan

- **File dihapus**: 3
- **File baru**: 3
- **File diubah**: 5
- **Lines of code dikurangi**: ~150 (cleanup)
- **Endpoint baru**: 1 (`/health`)
