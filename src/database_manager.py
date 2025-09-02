import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='database/attendance.db'):
        self.db_path = db_path
        self.initialize_database()
    
    def initialize_database(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                image_path TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                check_in TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, name, image_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (name, image_path) VALUES (?, ?)', (name, image_path))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    
    def mark_attendance(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        current_time = datetime.now()
        cursor.execute('INSERT INTO attendance (user_id, check_in) VALUES (?, ?)', 
                      (user_id, current_time))
        conn.commit()
        conn.close()
    
    def get_user_by_id(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def get_all_users(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        conn.close()
        return users
