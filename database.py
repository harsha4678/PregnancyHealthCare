import sqlite3

# Connect to the database (creates pregnancy.db if not exists)
conn = sqlite3.connect('pregnancy.db')
cur = conn.cursor()

# Create users table
cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    password TEXT
)
''')

# Create health_records table (fixed foreign key syntax)
cur.execute('''
CREATE TABLE IF NOT EXISTS health_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    file_name TEXT,
    file_path TEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Create symptoms table
cur.execute('''
CREATE TABLE IF NOT EXISTS symptoms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    symptom TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    advice TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Create appointments table
cur.execute('''
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    hospital_name TEXT,
    specialization TEXT,
    date TEXT,
    time TEXT,
    status TEXT DEFAULT 'Pending',
    reminder_sent INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')


# Commit and close connection
conn.commit()
conn.close()

print("Database initialized successfully.")
