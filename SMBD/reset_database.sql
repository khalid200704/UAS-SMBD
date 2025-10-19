-- Hapus database jika sudah ada
DROP DATABASE IF EXISTS yolo_edge;

-- Buat database baru
CREATE DATABASE yolo_edge;
USE yolo_edge;

-- Buat tabel devices
CREATE TABLE devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    last_status VARCHAR(50),
    last_active DATETIME,
    total_human_detection INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Buat tabel detections
CREATE TABLE detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    timestamp DATETIME NOT NULL,
    status VARCHAR(50) NOT NULL,
    jitter FLOAT,
    delay_ms FLOAT,
    human_count INT DEFAULT 0,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
);

-- Insert data device default
INSERT INTO devices (id, name, location, last_status, last_active, total_human_detection) 
VALUES (1, 'ESP32-CAM', 'Lokasi 1', 'OFFLINE', NULL, 0);

-- Tampilkan struktur tabel
SHOW TABLES;
DESCRIBE devices;
DESCRIBE detections;
