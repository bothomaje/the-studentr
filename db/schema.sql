CREATE DATABASE IF NOT EXISTS the_studentr
  DEFAULT  CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
USE the_studentr;

CREATE TABLE IF NOT EXISTS USERS (
  user_id CHAR(36) CHARACTER SET ascii,
  username VARCHAR(100) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARBINARY(255) NOT NULL,
  first_name VARCHAR(100) NOT NULL,
  surname VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS MODULES (
  module_id CHAR(36) CHARACTER SET ascii,
  user_id CHAR(36) CHARACTER SET ascii NOT NULL,
  module_code VARCHAR(16) NOT NULL,
  module_name VARCHAR(100) NOT NULL,
  year_mark_weight DECIMAL(5,2) CHECK (year_mark_weight >= 0 AND year_mark_weight <= 100) NOT NULL,
  exam_weight DECIMAL(5,2) CHECK (exam_weight >= 0 AND exam_weight <= 100) NOT NULL,
  min_assignments INT NOT NULL DEFAULT 1 CHECK (min_assignments > 0),
  min_year_mark DECIMAL(5,2) CHECK (min_year_mark >= 0 AND min_year_mark <= 100),
  exam_subminimum DECIMAL(5,2) CHECK (exam_subminimum >= 0 AND exam_subminimum <= 100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (module_id),
  FOREIGN KEY (user_id) REFERENCES USERS(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT user_module UNIQUE (user_id, module_code),
  CONSTRAINT CHECK (year_mark_weight + exam_weight = 100),
  INDEX idx_modules_user (user_id)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS  ASSIGNMENTS (
  assignment_id CHAR(36) CHARACTER SET ascii,
  module_id CHAR(36) CHARACTER SET ascii NOT NULL,
  category ENUM('Formative','Exam') NOT NULL,
  assignment_type ENUM('Quiz','Written assignment','Practical','Written exam','Take-Home exam') NOT NULL,
  assignment_title VARCHAR(120) NOT NULL,
  start_date DATE,
  due_date DATE NOT NULL,
  due_time TIME DEFAULT '23:59:00' NOT NULL,
  submit_date DATE,
  status ENUM('Not Started','In Progress','Done','Skipped') NOT NULL DEFAULT 'Not Started',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (assignment_id),
  FOREIGN KEY (module_id) REFERENCES MODULES(module_id) ON DELETE CASCADE ON UPDATE CASCADE,
  INDEX idx_asg_module_due (module_id, due_date),
  INDEX idx_asg_module_cat_due (module_id, category, due_date),
  INDEX idx_asg_module_status (module_id, status)
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS MARKS (
  mark_id CHAR(36) CHARACTER SET ascii,
  assignment_id CHAR(36) CHARACTER SET ascii UNIQUE NOT NULL,
  weight DECIMAL(5,2) CHECK (weight >= 0 AND weight <= 100) NOT NULL,
  score DECIMAL(5,2) CHECK (score >= 0 AND score <= 100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (mark_id),
  FOREIGN KEY (assignment_id) REFERENCES ASSIGNMENTS(assignment_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;
