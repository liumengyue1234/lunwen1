-- 初始管理员账号（密码: admin123，BCrypt加密）
INSERT INTO sys_user (username, password, real_name, email, role) 
VALUES ('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBpCFv9nGLqFOm', '管理员', 'admin@example.com', 'ADMIN')
ON CONFLICT DO NOTHING;

-- 测试普通用户（密码: user123）
INSERT INTO sys_user (username, password, real_name, email, role) 
VALUES ('liuxinyue', '$2a$10$UvZ8tTSzq8LGTlCPq5MZ8OjBgpnJQfvOMVUSLX.1FhXn6x9UGZXHC', '刘昕月', 'liuxinyue@example.com', 'USER')
ON CONFLICT DO NOTHING;
