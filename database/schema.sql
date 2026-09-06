CREATE DATABASE IF NOT EXISTS krushi_samruddhi_odisha
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE krushi_samruddhi_odisha;

-- ============================================================
-- DISTRICTS
-- ============================================================

CREATE TABLE IF NOT EXISTS districts (
    district_id INT AUTO_INCREMENT PRIMARY KEY,
    district_name_en VARCHAR(100) NOT NULL UNIQUE,
    district_name_od VARCHAR(100),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7)
);

-- ============================================================
-- BLOCKS
-- ============================================================

CREATE TABLE IF NOT EXISTS blocks (
    block_id INT AUTO_INCREMENT PRIMARY KEY,
    district_id INT NOT NULL,
    block_name_en VARCHAR(100) NOT NULL,
    block_name_od VARCHAR(100),

    CONSTRAINT fk_blocks_district
        FOREIGN KEY (district_id)
        REFERENCES districts(district_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    UNIQUE (district_id, block_name_en)
);

-- ============================================================
-- GRAM PANCHAYATS
-- ============================================================

CREATE TABLE IF NOT EXISTS gram_panchayats (
    gp_id INT AUTO_INCREMENT PRIMARY KEY,
    block_id INT NOT NULL,
    gp_name_en VARCHAR(150) NOT NULL,
    gp_name_od VARCHAR(150),

    CONSTRAINT fk_gp_block
        FOREIGN KEY (block_id)
        REFERENCES blocks(block_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    UNIQUE (block_id, gp_name_en)
);

-- ============================================================
-- VILLAGES
-- ============================================================

CREATE TABLE IF NOT EXISTS villages (
    village_id INT AUTO_INCREMENT PRIMARY KEY,
    gp_id INT NOT NULL,
    village_name_en VARCHAR(150) NOT NULL,
    village_name_od VARCHAR(150),
    lgd_code VARCHAR(50),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    area_sq_km DECIMAL(12,4),
    population INT,

    CONSTRAINT fk_village_gp
        FOREIGN KEY (gp_id)
        REFERENCES gram_panchayats(gp_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    UNIQUE (gp_id, village_name_en)
);

-- ============================================================
-- WEATHER DATA
-- ============================================================

CREATE TABLE IF NOT EXISTS weather_data (
    weather_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    village_id INT NOT NULL,
    observation_date DATE NOT NULL,
    temperature_c DECIMAL(6,2),
    rainfall_mm DECIMAL(10,2),
    humidity_percent DECIMAL(6,2),
    wind_speed_kmph DECIMAL(8,2),

    CONSTRAINT fk_weather_village
        FOREIGN KEY (village_id)
        REFERENCES villages(village_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    UNIQUE (village_id, observation_date)
);

-- ============================================================
-- RISK ALERTS
-- ============================================================

CREATE TABLE IF NOT EXISTS risk_alerts (
    alert_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    village_id INT NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    risk_level ENUM('Low', 'Medium', 'High') NOT NULL,
    alert_message TEXT,
    alert_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_alert_village
        FOREIGN KEY (village_id)
        REFERENCES villages(village_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX idx_blocks_district
    ON blocks(district_id);

CREATE INDEX idx_gp_block
    ON gram_panchayats(block_id);

CREATE INDEX idx_villages_gp
    ON villages(gp_id);

CREATE INDEX idx_villages_lgd
    ON villages(lgd_code);

CREATE INDEX idx_weather_date
    ON weather_data(observation_date);

CREATE INDEX idx_alert_village
    ON risk_alerts(village_id);

CREATE INDEX idx_alert_risk
    ON risk_alerts(risk_level);

CREATE INDEX idx_alert_active
    ON risk_alerts(is_active);