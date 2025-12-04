CREATE DATABASE IF NOT EXISTS yolo_edge;
USE yolo_edge;

-- Tabel Users untuk login (password hash bcrypt)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(100),
    role ENUM('admin', 'user') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    ip_address VARCHAR(50),
    total_human_detection INT DEFAULT 0,
    last_status VARCHAR(50),
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50),
    jitter FLOAT,
    delay_ms FLOAT,
    human_count INT DEFAULT 0,
    image LONGBLOB NULL,
    FOREIGN KEY (device_id) REFERENCES devices(id)
);

-- Data awal
INSERT INTO devices (device_name, ip_address, total_human_detection, last_status)
VALUES ('ESP32-CAM', '172.20.10.2', 0, 'inactive');

-- Admin user (password: admin123, hash bcrypt, contoh hash)
-- Ganti hash berikut jika ingin password berbeda
INSERT INTO users (username, password, email, fullname, role)
VALUES ('admin', '$2b$12$tGqA2Iy0uI3N8C7WZLvKTeWjYZOCyXafKRacErUzQnHqGj7Jh5uQy', 'admin@gmail.com', 'Administrator', 'admin');
