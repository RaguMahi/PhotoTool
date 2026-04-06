/*
  # Create Image Enhancement Studio Tables
  
  1. New Tables
    - `image_library` - Stores processed images with enhancement parameters
    - `template_library` - Stores phone frame templates
    - `job_templates` - Stores job configurations for merging screenshots with templates
*/

CREATE TABLE IF NOT EXISTS image_library (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  file_path TEXT NOT NULL,
  processing_params JSONB
);

CREATE TABLE IF NOT EXISTS template_library (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  file_path TEXT NOT NULL,
  default_params JSONB
);

CREATE TABLE IF NOT EXISTS job_templates (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  template_id INTEGER REFERENCES template_library(id),
  screenshot_path TEXT NOT NULL,
  alignment_params JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);