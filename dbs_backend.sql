CREATE DATABASE fajao_exam_bank_db;

USE fajao_exam_bank_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_premium BOOLEAN DEFAULT FALSE,
    premium_expiry DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    subject VARCHAR(50) NOT NULL,
    form_level VARCHAR(10) NOT NULL,
    exam_type VARCHAR(50) NOT NULL,
    is_premium BOOLEAN DEFAULT FALSE,
    filename VARCHAR(255) NOT NULL,
    file_size INT NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    uploaded_by INT NOT NULL,
    upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    download_count INT DEFAULT 0,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    plan_type ENUM('monthly', 'annual') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    transaction_id VARCHAR(100) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);