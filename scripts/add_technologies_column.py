import sqlite3
import os

DB_PATH = 'instance/pehchaan.db'

def add_technologies_column():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(projects)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'technologies' not in columns:
            print("Adding 'technologies' column to 'projects' table...")
            cursor.execute("ALTER TABLE projects ADD COLUMN technologies VARCHAR(255)")
            conn.commit()
            print("Column added successfully.")
        else:
            print("'technologies' column already exists.")
            
    except Exception as e:
        print(f"Error adding column: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    add_technologies_column()
