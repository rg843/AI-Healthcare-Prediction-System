-- PostgreSQL schema for Healthcare AI System
CREATE TABLE IF NOT EXISTS roles (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username VARCHAR(150) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  role_id INTEGER REFERENCES roles(id),
  full_name VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS patients (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  name VARCHAR(255) NOT NULL,
  age INTEGER,
  gender VARCHAR(20),
  weight FLOAT,
  height FLOAT,
  blood_group VARCHAR(10),
  address TEXT,
  medical_history TEXT,
  family_history TEXT,
  allergies TEXT,
  insurance JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS doctors (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  doctor_id VARCHAR(50) UNIQUE,
  name VARCHAR(255),
  qualification VARCHAR(255),
  experience INTEGER,
  department VARCHAR(255),
  availability JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS appointments (
  id SERIAL PRIMARY KEY,
  patient_id INTEGER REFERENCES patients(id),
  doctor_id INTEGER REFERENCES doctors(id),
  scheduled_at TIMESTAMPTZ NOT NULL,
  slot VARCHAR(50),
  status VARCHAR(50) DEFAULT 'pending',
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ehr (
  id SERIAL PRIMARY KEY,
  patient_id INTEGER REFERENCES patients(id),
  doctor_id INTEGER REFERENCES doctors(id),
  diagnosis TEXT,
  prescriptions JSONB,
  reports JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS beds (
  id SERIAL PRIMARY KEY,
  type VARCHAR(50),
  total INTEGER DEFAULT 0,
  occupied INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS resources (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  total INTEGER DEFAULT 0,
  available INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS model_metadata (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255),
  version VARCHAR(50),
  path VARCHAR(1024),
  metrics JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);
