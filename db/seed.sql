USE the_studentr;
START TRANSACTION;

--Insert test user into USERS table
INSERT INTO USERS (user_id, username, email, password_hash, first_name, surname)
VALUES ('000000000000000000000000000000000001', 'testuser1', 'testuser1@mail.com', '', 'Test', 'One') AS new
ON DUPLICATE KEY UPDATE email = new.email;

--Insert COS2611 and INF2611 modules into MODULES table
INSERT INTO MODULES (module_id, user_id, module_code, module_name, year_mark_weight, exam_weight, min_assignments)
VALUES
('100000000000000000000000000000000101', '000000000000000000000000000000000001', 'COS2611', 'Programming: Data Structures', 20, 80, 1),
('100000000000000000000000000000000102', '000000000000000000000000000000000001', 'INF2611', 'Visual Programming II', 30, 70, 1) AS new
ON DUPLICATE KEY UPDATE module_name = new.module_name;

-- Insert assignments for COS2611 into ASSIGNMENTS table
INSERT INTO ASSIGNMENTS (assignment_id, module_id, category, assignment_type, assignment_title, start_date, due_time, submit_date, status)
VALUES
('200000000000000000000000000000000101', '100000000000000000000000000000000101', 'Formative', 'Practical', 'Project 1', '2025-02-01', '2025-05-01', '2025-04-12', 'Done'),
('200000000000000000000000000000000102', '100000000000000000000000000000000101', 'Formative', 'Practical', 'Project 2', '2025-05-01', '2025-07-30', '2025-07-29', 'Done'),
('200000000000000000000000000000000102', '100000000000000000000000000000000101', 'Formative', 'Practical', 'Project 3', '2025-08-11', '2025-09-15', NULL, 'In Progress'),
('200000000000000000000000000000000102', '100000000000000000000000000000000101', 'Formative', 'Quiz', 'Quiz', '2025-09-01', '2025-10-01', NULL, 'Not Started'),
('200000000000000000000000000000000102', '100000000000000000000000000000000101', 'Exam', 'Practical', 'Practical Exam', NULL, '2025-11-01', NULL, 'Not Started'),
('200000000000000000000000000000000102', '100000000000000000000000000000000101', 'Exam', 'Quiz', 'Theory Exam', NULL, '2025-11-05', NULL, 'Not Started') AS new
ON DUPLICATE KEY UPDATE assignment_title = new.assignment_title;

-- Insert assignments for INF2611 into ASSIGNMENTS table
INSERT INTO ASSIGNMENTS (assignment_id, module_id, category, assignment_type, assignment_title, start_date, due_date, submit_date, status)
VALUES
('200000000000000000000000000000000102', '100000000000000000000000000000000102', 'Formative', 'Quiz', 'Assessment 1', '2025-03-21', '2025-05-16', '2025-05-01', 'Done'),
('200000000000000000000000000000000102', '100000000000000000000000000000000102', 'Formative', 'Quiz', 'Assessment 2', '2025-04-25', '2025-09-22', '2025-05-16', 'Done'),
('200000000000000000000000000000000102', '100000000000000000000000000000000102', 'Formative', 'Quiz', 'Assessment 3', '2025-06-09', '2025-09-22', '2025-09-10', 'Done'),
('200000000000000000000000000000000102', '100000000000000000000000000000000102', 'Formative', 'Practical', 'Assessment 4', '2025-08-04', '2025-09-16', NULL, 'In Progress'),
('200000000000000000000000000000000102', '100000000000000000000000000000000102', 'Exam', 'Quiz', 'Final Exam', NULL, '2025-11-03', NULL, 'Not Started') AS new
ON DUPLICATE KEY UPDATE assignment_title = new.assignment_title;
