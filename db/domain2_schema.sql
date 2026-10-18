-- Domain 2 uses Django's built-in auth migrations.
-- Run `python manage.py migrate` after configuring MySQL.
-- This project-specific table is equivalent to accounts.UserProfile.

USE library_db;

CREATE TABLE user_profiles (
  id BIGINT NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  student_code VARCHAR(30) NULL,
  phone VARCHAR(20) NOT NULL,
  date_of_birth DATE NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_user_profiles_user (user_id),
  UNIQUE KEY uq_user_profiles_student_code (student_code),
  CONSTRAINT fk_user_profiles_user FOREIGN KEY (user_id)
    REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB;
