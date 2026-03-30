import sqlite3
import os
from datetime import datetime

DATABASE = 'images_db.sqlite'

def get_db_connection():
    """Returns a new connection to the SQLite database with row_factory enabled."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema and performs simple migrations for status columns."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if table exists to see if we need to migrate or create a new one
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='processed_images'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                description TEXT DEFAULT '',
                image_path TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                error_msg TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        # Check if status column exists, if not, add it (simple migration)
        cursor.execute("PRAGMA table_info(processed_images)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'status' not in columns:
            cursor.execute("ALTER TABLE processed_images ADD COLUMN status TEXT DEFAULT 'completed'")
        if 'error_msg' not in columns:
            cursor.execute("ALTER TABLE processed_images ADD COLUMN error_msg TEXT")
            
    conn.commit()
    conn.close()

def save_image_record(filename, description, image_path, status='completed'):
    """Saves a new image record to the database and returns its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO processed_images (filename, description, image_path, status) VALUES (?, ?, ?, ?)',
        (filename, description, image_path, status)
    )
    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return last_id

def update_image_record(record_id, description, status='completed', error_msg=None):
    """Updates an existing image record with analysis results or error messages."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE processed_images SET description = ?, status = ?, error_msg = ? WHERE id = ?',
        (description, status, error_msg, record_id)
    )
    conn.commit()
    conn.close()

def get_all_records():
    """Retrieves all image records ordered by the creation date (newest first)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM processed_images ORDER BY created_at DESC')
    records = cursor.fetchall()
    conn.close()
    return [dict(row) for row in records]

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
