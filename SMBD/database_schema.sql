-- Database schema untuk sistem pemantauan edge computing YOLO
-- Jalankan script ini di MySQL untuk membuat database dan tabel yang diperlukan

-- Hapus database lama jika ingin reset (HATI-HATI: akan menghapus semua data)
-- DROP DATABASE IF EXISTS yolo_edge;

CREATE DATABASE IF NOT EXISTS yolo_edge;
USE yolo_edge;

-- Tabel untuk menyimpan informasi perangkat (ESP32-CAM)
CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    ip_address VARCHAR(45),
    total_human_detection INT DEFAULT 0,
    last_status VARCHAR(50) DEFAULT 'IDLE',
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel untuk menyimpan hasil deteksi real-time
CREATE TABLE IF NOT EXISTS detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    jitter FLOAT DEFAULT 0,
    delay_ms FLOAT NOT NULL,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_timestamp (timestamp),
    INDEX idx_device_timestamp (device_id, timestamp)
);

-- Insert data perangkat default
INSERT INTO devices (id, device_name, ip_address) VALUES 
(1, 'ESP32-CAM-01', '172.20.10.2') 
ON DUPLICATE KEY UPDATE 
device_name = VALUES(device_name), 
ip_address = VALUES(ip_address);

-- Cleanup: Hapus kolom yang tidak terpakai (jika ada dari versi lama)
ALTER TABLE detections DROP COLUMN IF EXISTS human_count;
ALTER TABLE detections DROP COLUMN IF EXISTS confidence;

-- Tampilkan struktur tabel
DESCRIBE devices;
DESCRIBE detections;

-- Tampilkan data devices
SELECT * FROM devices;
