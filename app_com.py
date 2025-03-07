from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Secret key for session management
app.secret_key = "my_super_secret_key_123"

# Database file
DATABASE = 'pregnancy.db'

# Upload folder setup
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Makes fetching data easier
    return conn

# Initialize the database with additional tables
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create users table if not exists
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        age INTEGER,
        weight REAL,
        height REAL,
        due_date TEXT,
        partner_name TEXT,
        partner_phone TEXT,
        profile_complete BOOLEAN DEFAULT 0
    )
    ''')
    
    # Create health_records table if not exists
    cur.execute('''
    CREATE TABLE IF NOT EXISTS health_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        file_name TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create symptoms table if not exists
    cur.execute('''
    CREATE TABLE IF NOT EXISTS symptoms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        symptom TEXT,
        advice TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create appointments table if not exists
    cur.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        doctor_name TEXT,
        date TEXT,
        time TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize DB before first request


# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        password = request.form['password']
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, phone, password) VALUES (?, ?, ?)", (name, phone, password))
        conn.commit()
        conn.close()
        
        flash("Registration successful! Please login.")
        return redirect(url_for('login'))
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE phone=? AND password=?", (phone, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['profile_complete'] = bool(user['profile_complete'])

            if not session['profile_complete']:
                flash("Please complete your profile to continue.", "warning")
                return redirect(url_for('profile'))

            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!", "danger")

    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id=?", (session['user_id'],)).fetchone()
    conn.close()

    if not user:
        flash("User not found. Please login again.", "danger")
        return redirect(url_for('login'))

    days_remaining = None
    if user['due_date']:
        due_date = datetime.strptime(user['due_date'], '%Y-%m-%d').date()
        today = date.today()
        days_remaining = (due_date - today).days
        if days_remaining < 0:
            days_remaining = 0

    return render_template('dashboard.html', 
                           name=user['name'], 
                           days_remaining=days_remaining, 
                           due_date=user['due_date'])

# Profile Route
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()

    if not user:
        flash("User not found. Please login again.", "danger")
        conn.close()
        return redirect(url_for('login'))

    if request.method == 'POST':
        age = request.form['age']
        weight = request.form['weight']
        height = request.form['height']
        due_date = request.form['due_date']
        partner_name = request.form.get('partner_name', '')
        partner_phone = request.form.get('partner_phone', '')

        conn.execute('''
            UPDATE users
            SET age = ?, weight = ?, height = ?, due_date = ?, 
                partner_name = ?, partner_phone = ?, profile_complete = 1
            WHERE id = ?
        ''', (age, weight, height, due_date, partner_name, partner_phone, session['user_id']))
        conn.commit()
        conn.close()

        session['profile_complete'] = True
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    days_remaining = None
    if user['due_date']:
        due_date_obj = datetime.strptime(user['due_date'], '%Y-%m-%d').date()
        days_remaining = (due_date_obj - date.today()).days

    return render_template('profile.html', user=user, days_remaining=days_remaining)
# Upload Health Record
@app.route('/upload_record', methods=['GET', 'POST'])
def upload_record():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO health_records (user_id, file_name) VALUES (?, ?)", (session['user_id'], filename))
            conn.commit()
            conn.close()
            
            flash("File uploaded successfully!")
            return redirect(url_for('records'))
    return render_template('upload_record.html')

# View Records
@app.route('/records')
def records():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM health_records WHERE user_id=?", (session['user_id'],))
    records = cur.fetchall()
    conn.close()

    return render_template('records.html', records=records)

# Symptom Checker
@app.route('/symptom_checker', methods=['GET', 'POST'])
def symptom_checker():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    advice = None
    if request.method == 'POST':
        symptom = request.form['symptom']
        advice = "Drink plenty of water and rest."

        if 'nausea' in symptom.lower():
            advice = "Eat small frequent meals, avoid spicy foods."
        elif 'headache' in symptom.lower():
            advice = "Stay hydrated and avoid stress."

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO symptoms (user_id, symptom, advice) VALUES (?, ?, ?)", (session['user_id'], symptom, advice))
        conn.commit()
        conn.close()
    
    return render_template('symptom_checker.html', advice=advice)

# Diet Plan Route
@app.route('/diet_plan')
def diet_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    sample_diet = {
        "Breakfast": "Oats with fruits and milk",
        "Lunch": "Rice, Dal, Vegetables, Curd",
        "Dinner": "Whole wheat roti, Green leafy curry, Soup"
    }

    return render_template('diet_plan.html', diet=sample_diet)

# Book Appointment
@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        doctor_name = request.form['doctor']
        date = request.form['date']
        time = request.form['time']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO appointments (user_id, doctor_name, date, time) VALUES (?, ?, ?, ?)", (session['user_id'], doctor_name, date, time))
        conn.commit()
        conn.close()
        
        flash("Appointment booked successfully!")
        return redirect(url_for('appointments'))
    
    return render_template('book_appointment.html')

# View Appointments
@app.route('/appointments')
def appointments():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM appointments WHERE user_id=?", (session['user_id'],))
    appointments = cur.fetchall()
    conn.close()
    
    return render_template('appointments.html', appointments=appointments)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Run the App
if __name__ == '__main__':
    app.run(debug=True)