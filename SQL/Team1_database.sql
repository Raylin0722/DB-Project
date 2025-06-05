CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50),
    school_email VARCHAR(100) UNIQUE,
    password_hash TEXT,
    department VARCHAR(50),
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'member'
);
CREATE TABLE tempusers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    school_email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    department VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE lostitems (
    lost_id INT PRIMARY KEY,
    item_name VARCHAR(100),
    category VARCHAR(50),
    lost_location VARCHAR(100),
    lost_time DATETIME,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    notification_period INT,
    remark TEXT,
    status VARCHAR(20),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE founditems (
    found_id INT PRIMARY KEY,
    item_name VARCHAR(100),
    category VARCHAR(50),
    found_location VARCHAR(100),
    found_time DATETIME,
    storage_location VARCHAR(100),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(100),
    remark TEXT,
    status VARCHAR(20),
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE reports (
    report_id INT PRIMARY KEY,
    target_id INT,
    FOREIGN KEY (target_id) REFERENCES founditems(found_id) ON DELETE CASCADE,
    description TEXT,
    status VARCHAR(20),
    created_at DATETIME
);

CREATE TABLE matches (
    lost_id INT,
    found_id INT,
    match_time DATETIME,
    status VARCHAR(20),
    PRIMARY KEY (lost_id, found_id),
    FOREIGN KEY (lost_id) REFERENCES lostitems(lost_id) ON DELETE CASCADE,
    FOREIGN KEY (found_id) REFERENCES founditems(found_id) ON DELETE CASCADE
);

CREATE TABLE passwordresetrequests (
    request_id INT PRIMARY KEY AUTO_INCREMENT,
    token VARCHAR(255),
    expiry DATETIME,
    used BOOLEAN,
    created_at DATETIME,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE notifications (
    notification_id INT PRIMARY KEY,
    message TEXT,
    delivered BOOLEAN,
    created_at DATETIME,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE flags (
    report_id INT,
    found_id INT,
    PRIMARY KEY (report_id, found_id),
    FOREIGN KEY (report_id) REFERENCES reports(report_id) ON DELETE CASCADE,
    FOREIGN KEY (found_id) REFERENCES founditems(found_id) ON DELETE CASCADE
);
