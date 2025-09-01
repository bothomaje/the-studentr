USE the_studentr;
START TRANSACTION;

INSERT INTO USERS (user_id, username, email, password_hash, first_name, surname)
VALUES ('000000000000000000000000000000000001', 'testuser1', 'testuser1@mail.com', '', 'Test', 'One',) AS new
ON DUPLICATE KEY UPDATE email=new.email;

INSERT INTO MODULES (module_id, user_id, module_code, module_name, year_mark_weight, exam_weight, min_assignments)
VALUES
('000000000000000000000000000000000101', '000000000000000000000000000000000001', 'COS2611', 'Programming: Data Structures', 20, 80, 1),
('000000000000000000000000000000000102', '000000000000000000000000000000000001', 'INF2611', 'Visual Programming II', 30, 70, 1) AS new
ON DUPLICATE KEY UPDATE module_name=new.module_name;