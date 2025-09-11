USE the_studentr;
START TRANSACTION;

-- Insert test user into USERS table
INSERT INTO users (user_id, username, email, password_hash, first_name, surname)
VALUES (
    '8a3b2e4c-5d6f-7a89-b012-3456789abcde',
    'testuser1',
    'testuser1@mail.com',
    '$2b$12$y5PqU9p.5M3T3d9v8Zk1AOe45z8onh5b9uC3C1m8EoS9Oq2g3sZha',
    'Test',
    'One'
) AS new
ON DUPLICATE KEY UPDATE email = new.email;

-- Insert COS2611 and INF2611 modules into MODULES table
INSERT INTO modules (
    module_id,
    user_id,
    module_code,
    module_name,
    year_mark_weight,
    exam_weight,
    min_assignments
)
VALUES
(
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7081',
    '8a3b2e4c-5d6f-7a89-b012-3456789abcde',
    'COS2611',
    'Programming: Data Structures',
    20,
    80,
    1
),
(
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7082',
    '8a3b2e4c-5d6f-7a89-b012-3456789abcde',
    'INF2611',
    'Visual Programming II',
    30,
    70,
    1
) AS new
ON DUPLICATE KEY UPDATE module_name = new.module_name;

-- Insert assignments for COS2611 into ASSIGNMENTS table
INSERT INTO assignments (
    assignment_id,
    module_id,
    category,
    assignment_type,
    assignment_title,
    start_date,
    due_date,
    submit_date,
    status
)
VALUES
(
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e001',
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7081',
    'Formative',
    'Practical',
    'Project 1',
    '2025-02-01',
    '2025-05-01',
    '2025-04-12',
    'Done'
),
(
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e002',
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7081',
    'Formative',
    'Practical',
    'Project 2',
    '2025-05-01',
    '2025-07-30',
    '2025-07-29',
    'Done'
),
(
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e003',
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7081',
    'Formative',
    'Practical',
    'Project 3',
    '2025-08-11',
    '2025-09-15',
    NULL,
    'In Progress'
),
(
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e004',
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7081',
    'Formative',
    'Quiz',
    'Quiz',
    '2025-09-01',
    '2025-10-01',
    NULL,
    'Not Started'
),
(
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e005',
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7081',
    'Exam',
    'Practical',
    'Practical Exam',
    NULL,
    '2025-11-01',
    NULL,
    'Not Started'
),
(
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e006',
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7081',
    'Exam',
    'Quiz',
    'Theory Exam',
    NULL,
    '2025-11-05',
    NULL,
    'Not Started'
) AS new
ON DUPLICATE KEY UPDATE assignment_title = new.assignment_title;

-- Insert assignments for INF2611 into ASSIGNMENTS table
INSERT INTO assignments (
    assignment_id,
    module_id,
    category,
    assignment_type,
    assignment_title,
    start_date,
    due_date,
    submit_date,
    status
)
VALUES
(
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e007',
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7082',
    'Formative',
    'Quiz',
    'Assessment 1',
    '2025-03-21',
    '2025-05-16',
    '2025-05-01',
    'Done'
),
(
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e008',
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7082',
    'Formative',
    'Quiz',
    'Assessment 2',
    '2025-04-25',
    '2025-09-22',
    '2025-05-16',
    'Done'
),
(
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e009',
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7082',
    'Formative',
    'Quiz',
    'Assessment 3',
    '2025-06-09',
    '2025-09-22',
    '2025-09-10',
    'Done'
),
(
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e010',
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7082',
    'Formative',
    'Practical',
    'Assessment 4',
    '2025-08-04',
    '2025-09-16',
    NULL,
    'In Progress'
),
(
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e011',
    '3f4a1b2c-3d4e-5f60-a1b2-3c4d5e6f7082',
    'Exam',
    'Quiz',
    'Final Exam',
    NULL,
    '2025-11-03',
    NULL,
    'Not Started'
) AS new
ON DUPLICATE KEY UPDATE assignment_title = new.assignment_title;

-- Insert marks into MARKS table
INSERT INTO marks (mark_id, assignment_id, weight, score)
VALUES
(
    '2aa1a2a3-a4a5-a6a7-a8a9-a0b1c2d3e401',
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e001',
    25,
    64
),
(
    '2aa1a2a3-a4a5-a6a7-a8a9-a0b1c2d3e402',
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e002',
    25,
    82
),
(
    '2aa1a2a3-a4a5-a6a7-a8a9-a0b1c2d3e403',
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e003',
    25,
    NULL
),
(
    '2aa1a2a3-a4a5-a6a7-a8a9-a0b1c2d3e404',
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e004',
    25,
    NULL
),
(
    '2aa1a2a3-a4a5-a6a7-a8a9-a0b1c2d3e405',
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e005',
    40,
    NULL
),
(
    '2aa1a2a3-a4a5-a6a7-a8a9-a0b1c2d3e406',
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e006',
    60,
    NULL
),
(
    '2aa1a2a3-a4a5-a6a7-a8a9-a0b1c2d3e407',
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e007',
    20,
    49
),
(
    '2aa1a2a3-a4a5-a6a7-a8a9-a0b1c2d3e408',
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e008',
    20,
    72
),
(
    '2aa1a2a3-a4a5-a6a7-a8a9-a0b1c2d3e409',
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e009',
    20,
    69
),
(
    '2aa1a2a3-a4a5-a6a7-a8a9-a0b1c2d3e410',
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e010',
    40,
    NULL
),
(
    '2aa1a2a3-a4a5-a6a7-a8a9-a0b1c2d3e411',
    '0c1d2e3f-4051-6273-8495-a6b7c8d9e011',
    100,
    NULL
) AS new
ON DUPLICATE KEY UPDATE weight = new.weight, score = new.score;

COMMIT;
