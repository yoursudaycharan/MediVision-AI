import sqlite3
from datetime import datetime

def init_database():
    """Create database tables if they don't exist"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()
    
    # Patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Medical records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            image_path TEXT,
            diagnosis TEXT,
            severity INTEGER,
            health_tips TEXT,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    ''')
    
    # Medicines table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            medicine_name TEXT,
            dosage TEXT,
            frequency TEXT,
            start_date DATE,
            end_date DATE,
            reminder_time TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def add_patient(name, age, gender, phone):
    """Add a new patient"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO patients (name, age, gender, phone) VALUES (?, ?, ?, ?)',
        (name, age, gender, phone)
    )
    conn.commit()
    patient_id = cursor.lastrowid
    conn.close()
    return patient_id

def save_medical_record(patient_id, image_path, diagnosis, severity, health_tips):
    """Save a medical analysis record"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO medical_records (patient_id, image_path, diagnosis, severity, health_tips) VALUES (?, ?, ?, ?, ?)',
        (patient_id, image_path, diagnosis, severity, health_tips)
    )
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id

def get_patient_records(patient_id):
    """Get all medical records for a patient"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM medical_records WHERE patient_id = ? ORDER BY analysis_date DESC',
        (patient_id,)
    )
    records = cursor.fetchall()
    conn.close()
    return records

def add_medicine(patient_id, medicine_name, dosage, frequency, reminder_time, start_date, end_date):
    """Add a new medicine reminder"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO medicines (patient_id, medicine_name, dosage, frequency, reminder_time, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (patient_id, medicine_name, dosage, frequency, reminder_time, start_date, end_date)
    )
    conn.commit()
    medicine_id = cursor.lastrowid
    conn.close()
    return medicine_id

def get_patient_medicines(patient_id):
    """Get all medicines for a patient"""
    conn = sqlite3.connect('medical_assistant.db')
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM medicines WHERE patient_id = ? ORDER BY reminder_time',
        (patient_id,)
    )
    medicines = cursor.fetchall()
    conn.close()
    return medicines