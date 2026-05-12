-- 用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(50) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    real_name   VARCHAR(50),
    email       VARCHAR(100),
    role        VARCHAR(20) DEFAULT 'USER',
    status      TINYINT DEFAULT 1,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 检测任务表
CREATE TABLE IF NOT EXISTS detection_task (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    task_name       VARCHAR(200),
    image_name      VARCHAR(255) NOT NULL,
    image_path      VARCHAR(500) NOT NULL,
    model_name      VARCHAR(50) DEFAULT 'yolov8s',
    conf_threshold  FLOAT DEFAULT 0.25,
    status          VARCHAR(20) DEFAULT 'PENDING',
    detect_count    INT DEFAULT 0,
    result_image    VARCHAR(500),
    result_json     TEXT,
    create_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finish_time     TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES sys_user(id)
);

-- 检测结果详情表
CREATE TABLE IF NOT EXISTS detection_result (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    task_id     BIGINT NOT NULL,
    label       VARCHAR(100),
    confidence  FLOAT,
    x1          FLOAT,
    y1          FLOAT,
    x2          FLOAT,
    y2          FLOAT,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES detection_task(id)
);
