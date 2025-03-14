from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file,jsonify, g
import sqlite3
import os
from werkzeug.utils import secure_filename
from hospital_utils import get_hospitals
from datetime import datetime, timedelta

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
    conn.row_factory = sqlite3.Row
    return conn

# Landing Route
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/home')
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
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials!")
    return render_template('login.html')




# Dashboard Route


@app.route('/dashboard')
def dashboard():
    
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not authenticated
    return render_template('dashboard.html', name=session.get('name', 'User'))  

# Upload Health Record
@app.route('/upload_record', methods=['GET', 'POST'])
def upload_record():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file part in request.")
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash("No file selected.")
            return redirect(request.url)

        filename = f"user_{session['user_id']}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO health_records (user_id, file_name, file_path)
            VALUES (?, ?, ?)
        ''', (session['user_id'], filename, filepath))
        conn.commit()
        conn.close()

        flash("File uploaded successfully!")
        return redirect(url_for('records'))

    return render_template('upload_record.html')

# View Records (with download link)
@app.route('/records')
def records():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT file_name, upload_date 
        FROM health_records 
        WHERE user_id=?
    ''', (session['user_id'],))
    records = cur.fetchall()
    conn.close()

    return render_template('records.html', records=records)

# Download File Route
@app.route('/download/<filename>')
def download_file(filename):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT file_path 
        FROM health_records 
        WHERE user_id=? AND file_name=?
    ''', (session['user_id'], filename))
    record = cur.fetchone()
    conn.close()

    if record and os.path.exists(record['file_path']):
        return send_file(record['file_path'], as_attachment=True)
    else:
        flash("File not found or unauthorized.")
        return redirect(url_for('records'))

# Symptom Checker Route (corrected)
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
        cur.execute("INSERT INTO symptoms (user_id, symptom, advice) VALUES (?, ?, ?)", 
                    (session['user_id'], symptom, advice))
        conn.commit()
        conn.close()

    return render_template('symptom_checker.html', advice=advice)

# Diet Plan Route
@app.route('/diet_plan', methods=['GET', 'POST'])
def diet_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Predefined options
    trimesters = ['First Trimester', 'Second Trimester', 'Third Trimester']
    health_conditions = ['None', 'Gestational Diabetes', 'Hypertension', 'Anemia', 'Nausea', 'Constipation']
    diets = ['Vegetarian', 'Vegan', 'Non-Vegetarian']
    cultures = ['Indian', 'Mediterranean', 'Western', 'Asian']

    # Default selected values
    selected_trimester = None
    selected_condition = None
    selected_diet = None
    selected_culture = None
    selected_plan = None

    if request.method == 'POST':
        selected_trimester = request.form['trimester']
        selected_condition = request.form['condition']
        selected_diet = request.form['diet']
        selected_culture = request.form['culture']

        # Generate diet plan based on inputs
        selected_plan = generate_diet_plan(selected_trimester, selected_condition, selected_diet, selected_culture)

    return render_template(
        'diet_plan.html',
        trimesters=trimesters,
        health_conditions=health_conditions,
        diets=diets,
        cultures=cultures,
        selected_plan=selected_plan,
        selected_trimester=selected_trimester,
        selected_condition=selected_condition,
        selected_diet=selected_diet,
        selected_culture=selected_culture
    )

def generate_diet_plan(trimester, condition, diet_type, culture):
    # 🌱 Start with trimester-specific meals (base diet)
    diet = {}

    if trimester == "First Trimester":
        diet = {
            "Breakfast": "Whole grain toast with avocado & boiled egg",
            "Snack": "Ginger tea with crackers",
            "Lunch": "Vegetable soup with whole grain bread",
            "Evening Snack": "Fruit salad with almonds",
            "Dinner": "Light khichdi with mint chutney",
        }
    elif trimester == "Second Trimester":
        diet = {
            "Breakfast": "Oats with chia seeds, banana, and walnuts",
            "Snack": "Greek yogurt with berries",
            "Lunch": "Grilled chicken with quinoa and spinach salad",
            "Evening Snack": "Boiled egg with flaxseed",
            "Dinner": "Palak paneer with brown rice",
        }
    elif trimester == "Third Trimester":
        diet = {
            "Breakfast": "Ragi porridge with dates & almonds",
            "Snack": "Milk with dry fruits",
            "Lunch": "Lentil curry with spinach and brown rice",
            "Evening Snack": "Sesame laddoo with coconut water",
            "Dinner": "Stuffed paratha with vegetable soup",
        }

    # 💉 Layer: Health Condition Adjustments
    if condition == "Gestational Diabetes":
        diet.update({
            "Breakfast": "Oats with chia, flaxseed & cinnamon (low GI)",
            "Snack": "Roasted chickpeas and cucumber sticks",
            "Lunch": "Grilled chicken with quinoa and leafy greens (low GI)",
            "Evening Snack": "Nuts, seeds, and berries (low sugar)",
        })
    elif condition == "Hypertension":
        diet.update({
            "Breakfast": "Banana smoothie with flaxseed",
            "Snack": "Watermelon salad with mint",
            "Lunch": "Grilled salmon with sweet potato & spinach",
            "Evening Snack": "Yogurt with flaxseed",
        })
    elif condition == "Anemia":
        diet.update({
            "Breakfast": "Beetroot and carrot smoothie",
            "Snack": "Dates stuffed with almonds",
            "Lunch": "Spinach dal with brown rice",
            "Evening Snack": "Pomegranate juice",
        })
    elif condition == "Nausea":
        diet.update({
            "Breakfast": "Dry toast with ginger lemon tea",
            "Snack": "Crackers with nut butter",
            "Lunch": "Light vegetable broth with rice crackers",
        })
    elif condition == "Constipation":
        diet.update({
            "Breakfast": "Flaxseed oatmeal with prunes",
            "Snack": "Papaya cubes with lemon",
            "Lunch": "Palak curry with brown rice",
            "Evening Snack": "Chia pudding with mango",
        })

    # 🌿 Layer: Dietary Preference (only apply if needed)
    if diet_type == "Vegetarian":
        diet.update({
            "Lunch": "Palak paneer with quinoa",
            "Dinner": "Rajma curry with brown rice & salad",
        })
    elif diet_type == "Vegan":
        diet.update({
            "Lunch": "Chickpea quinoa salad",
            "Dinner": "Tofu stir fry with millet",
        })
    elif diet_type == "Non-Vegetarian":
        diet.update({
            "Lunch": "Chicken curry with brown rice",
            "Dinner": "Grilled fish with roasted vegetables",
        })

    # 🌎 Layer: Cultural Customization
    if culture == "Indian":
        diet.update({
            "Breakfast": "Poha with peanuts & curry leaves",
            "Lunch": "Dal tadka with roti and vegetable sabzi",
            "Dinner": "Aloo methi with curd and roti",
        })
    elif culture == "Mediterranean":
        diet.update({
            "Breakfast": "Greek yogurt with figs, walnuts & honey",
            "Lunch": "Falafel bowl with hummus & tabbouleh",
            "Dinner": "Grilled eggplant with tahini sauce and couscous",
        })
    elif culture == "Western":
        diet.update({
            "Breakfast": "Scrambled eggs with avocado toast",
            "Lunch": "Chicken Caesar salad",
            "Dinner": "Baked salmon with quinoa and vegetables",
        })
    elif culture == "Asian":
        diet.update({
            "Breakfast": "Rice porridge with vegetables",
            "Lunch": "Stir-fried tofu with vegetables & rice",
            "Dinner": "Miso soup with vegetable sushi (cooked options)",
        })

    # 💧 Final touch: Hydration (always same)
    diet["Hydration"] = "At least 10 glasses of water, including coconut water & herbal teas."

    return diet


# Book Appointment


@app.route('/book_appointment', methods=['GET', 'POST'])
def book_appointment():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    specializations = [
        "General Physical", "Neurologist", "Dermatologist", "Cardiologist",
        "Orthopedist", "Pediatrician", "Gynecologist", "Psychiatrist",
        "Dentist", "Oncologist", "Endocrinologist", "Ophthalmologist",
        "Urologist", "Gastroenterologist", "Pulmonologist", "ENT",
        "Rheumatologist", "Radiologist", "Nephrologist", "Allergist", "Surgeon"
    ]

    hospitals = []

    if request.method == 'POST':
        specialization = request.form['specialization']
        location = request.form['location']

        # Fetch real hospitals
        result = get_hospitals(location=location, specialization=specialization)
        hospitals = result.get('hospitals', [])
        if 'error' in result:
            flash(result['error'])

        if 'confirm' in request.form:
            hospital_name = request.form['hospital_name']
            date = request.form['date']
            time = request.form['time']

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO appointments (user_id, hospital_name, specialization, date, time)
                VALUES (?, ?, ?, ?, ?)
            ''', (session['user_id'], hospital_name, specialization, date, time))
            conn.commit()
            conn.close()

            flash(f"Appointment booked at {hospital_name} on {date} at {time}.")
            return redirect(url_for('appointments'))

    return render_template('book_appointment.html', specializations=specializations, hospitals=hospitals)

# View Appointments
@app.route('/appointments')
def appointments():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT id, hospital_name, specialization, date, time, status 
        FROM appointments 
        WHERE user_id=?
    ''', (session['user_id'],))
    appointments = cur.fetchall()
    conn.close()

    return render_template('appointments.html', appointments=appointments)

def get_exercises():
    conn = sqlite3.connect("pregnancy.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, image, reps FROM exercises")
    exercises = [{"name": row[0], "image": row[1], "reps": row[2]} for row in cursor.fetchall()]
    conn.close()
    return exercises

# Route for the Exercises Page
@app.route('/exercises')
def exercises():
    exercises_list = get_exercises()
    return render_template("exercises.html", exercises=exercises_list)


# Pregnancy Tracker Page
@app.route('/pregnancy')
def pregnancy():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, date_type, input_date, calculated_due_date FROM pregnancy_records')
    pregnancy_data = cur.fetchall()
    conn.close()
    return render_template('pregnancy.html', pregnancy_data=pregnancy_data)

# Baby size data by week
BABY_SIZE_DATA = {
    1: {'size': '0.1 mm', 'weight': 'too small to weigh', 'comparison': 'Invisible to naked eye'},
    2: {'size': '0.2 mm', 'weight': 'too small to weigh', 'comparison': 'Poppy seed'},
    3: {'size': '0.9 mm', 'weight': 'too small to weigh', 'comparison': 'Sesame seed'},
    4: {'size': '2.5 mm', 'weight': '0.001g', 'comparison': 'Rice grain'},
    5: {'size': '5 mm', 'weight': '0.05g', 'comparison': 'Apple seed'},
    6: {'size': '8 mm', 'weight': '0.2g', 'comparison': 'Sweet pea'},
    7: {'size': '13 mm', 'weight': '1g', 'comparison': 'Blueberry'},
    8: {'size': '16 mm', 'weight': '1.5g', 'comparison': 'Raspberry'},
    9: {'size': '23 mm', 'weight': '2.5g', 'comparison': 'Green olive'},
    10: {'size': '31 mm', 'weight': '4g', 'comparison': 'Prune'},
    11: {'size': '41 mm', 'weight': '7g', 'comparison': 'Fig'},
    12: {'size': '53 mm', 'weight': '14g', 'comparison': 'Lime'},
    13: {'size': '74 mm', 'weight': '23g', 'comparison': 'Lemon'},
    14: {'size': '87 mm', 'weight': '43g', 'comparison': 'Orange'},
    15: {'size': '97 mm', 'weight': '70g', 'comparison': 'Apple'},
    16: {'size': '116 mm', 'weight': '100g', 'comparison': 'Avocado'},
    17: {'size': '133 mm', 'weight': '140g', 'comparison': 'Pear'},
    18: {'size': '144 mm', 'weight': '190g', 'comparison': 'Bell pepper'},
    19: {'size': '152 mm', 'weight': '240g', 'comparison': 'Mango'},
    20: {'size': '160 mm', 'weight': '300g', 'comparison': 'Banana'},
    # ... Add data for weeks 21-40
}

@app.route('/calculate_due_date', methods=['POST'])
def calculate_due_date():
    try:
        date_type = request.form.get('date_type')
        input_date = datetime.strptime(request.form.get('input_date'), '%Y-%m-%d')
        today = datetime.now()

        # Calculate conception and due dates based on input type
        if date_type == 'Ultrasound':
            # Get weeks and days from ultrasound measurements
            us_weeks = int(request.form.get('us_weeks', 0))
            us_days = int(request.form.get('us_days', 0))
            
            # Calculate total days of pregnancy at ultrasound
            total_pregnancy_days = (us_weeks * 7) + us_days
            
            # Calculate conception date by subtracting pregnancy length from ultrasound date
            # and adding 14 days (LMP to conception offset)
            conception_date = input_date - timedelta(days=total_pregnancy_days-14)
            
            # Calculate due date from conception date
            due_date = conception_date + timedelta(days=266)
        elif date_type == 'LMP':
            cycle_length = int(request.form.get('cycle_length', 28))
            ovulation_day = cycle_length - 14
            conception_date = input_date + timedelta(days=ovulation_day)
            due_date = input_date + timedelta(days=280)
        elif date_type == 'Conception Date':
            conception_date = input_date
            due_date = input_date + timedelta(days=266)
        elif date_type == 'Due Date':
            due_date = input_date
            conception_date = input_date - timedelta(days=266)
        elif date_type == 'IVF Transfer Date':
            embryo_age = int(request.form.get('embryo_age', 3))
            conception_date = input_date - timedelta(days=embryo_age)
            due_date = conception_date + timedelta(days=266)
        
        # Calculate current week and days remaining
        days_pregnant = (today - conception_date).days + 14  # Add 14 days as pregnancy is counted from LMP
        current_week = (days_pregnant // 7) + 1
        days_remaining = (due_date - today).days

        # Determine trimester
        if current_week <= 13:
            trimester = "First Trimester"
        elif current_week <= 26:
            trimester = "Second Trimester"
        else:
            trimester = "Third Trimester"

        # Get baby size information
        size_info = BABY_SIZE_DATA.get(current_week, {
            'size': 'Not available',
            'weight': 'Not available',
            'comparison': 'Not available'
        })
        baby_size = f"{size_info['size']} and {size_info['weight']} (about the size of a {size_info['comparison']})"

        return jsonify({
            'due_date': due_date.strftime('%B %d, %Y'),
            'current_week': current_week,
            'trimester': trimester,
            'baby_size': baby_size,
            'conception_date': conception_date.strftime('%B %d, %Y'),
            'days_remaining': days_remaining,
            'message': get_week_message(current_week)
        })

    except Exception as e:
        return jsonify({'error': str(e)})

def get_week_message(week):
    """Return a specific message based on the current week of pregnancy."""
    if week < 1:
        return "Please check your dates."
    elif week < 4:
        return "Early pregnancy - Implantation is occurring."
    elif week < 8:
        return "Major organs and structures are beginning to form."
    elif week < 13:
        return "First trimester - Baby's basic body structure is developing."
    elif week < 27:
        return "Second trimester - Period of rapid growth and development."
    elif week < 37:
        return "Third trimester - Baby is gaining weight and preparing for birth."
    else:
        return "Full term - Baby could arrive any day now!"

@app.route('/weight_gain_calculator', methods=['GET', 'POST'])
def weight_gain_calculator():
    result = None
    if request.method == 'POST':
        try:
            height_ft = float(request.form.get('height_ft', 0))
            height_in = float(request.form.get('height_in', 0))
            current_weight = float(request.form.get('current_weight', 0))
            pre_pregnancy_weight = float(request.form.get('pre_pregnancy_weight', 0))
            week = int(request.form.get('week', 0))
            pregnant_with_twins = request.form.get('twins') == 'on'

            # Convert height to meters
            height_m = ((height_ft * 12) + height_in) * 0.0254
            bmi = pre_pregnancy_weight / (height_m ** 2)

            # Recommended weight gain range based on IOM guidelines
            if bmi < 18.5:
                weight_gain_range = (28, 40)  # Underweight
            elif 18.5 <= bmi < 24.9:
                weight_gain_range = (25, 35)  # Normal weight
            elif 25 <= bmi < 29.9:
                weight_gain_range = (15, 25)  # Overweight
            else:
                weight_gain_range = (11, 20)  # Obese

            if pregnant_with_twins:
                weight_gain_range = (weight_gain_range[0] + 10, weight_gain_range[1] + 15)

            # Calculate expected weight at given week
            expected_weight_min = pre_pregnancy_weight + (weight_gain_range[0] * (week / 40))
            expected_weight_max = pre_pregnancy_weight + (weight_gain_range[1] * (week / 40))

            result = {
                "bmi": round(bmi, 1),
                "weight_gain_range": f"{weight_gain_range[0]} - {weight_gain_range[1]} lbs",
                "expected_weight_range": f"{round(expected_weight_min, 1)} - {round(expected_weight_max, 1)} lbs"
            }

        except ValueError:
            result = {"error": "Invalid input. Please enter valid numbers."}

    return render_template('weight_gain_calculator.html', result=result)
# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))



# Profile page route
@app.route('/profile1', methods=['GET'])
def profile1():
    if 'user_id' not in session:
        session['user_id'] = 1  # Placeholder (Assume user_id = 1 for testing)
    
    user_id = session['user_id']
    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch user profile data
    cur.execute("SELECT * FROM pregnancy_profile WHERE user_id = ?", (user_id,))
    profile = cur.fetchone()
    conn.close()

    return render_template('profile1.html', profile=profile)

# Save or update pregnancy profile data
@app.route('/save_profile', methods=['POST'])
def save_profile():
    if 'user_id' not in session:
        session['user_id'] = 1  # Placeholder user authentication
    
    user_id = session['user_id']
    
    # Collect form data
    data = (
        request.form['due_date'],
        request.form['last_menstrual_period'],
        request.form.get('previous_pregnancies', 0),
        request.form.get('live_births', 0),
        request.form.get('miscarriages', 0),
        request.form.get('current_week', 0),
        request.form.get('doctor_name', ''),
        request.form.get('doctor_contact', ''),
        request.form.get('hospital_name', ''),
        request.form.get('hospital_contact', ''),
        request.form.get('blood_type', ''),
        request.form.get('allergies', ''),
        request.form.get('medications', ''),
        request.form.get('pre_existing_conditions', ''),
        request.form.get('weight', 0),
        request.form.get('height', 0),
        request.form.get('diet', ''),
        request.form.get('exercise', ''),
        request.form.get('smoking_status', ''),
        request.form.get('alcohol_consumption', ''),
        request.form.get('caffeine_intake', ''),
        request.form.get('stress_levels', ''),
        request.form.get('emotional_wellbeing', ''),
        request.form.get('partner_name', ''),
        request.form.get('partner_contact', ''),
        request.form.get('emergency_contact', ''),
        request.form.get('birth_preferences', ''),
        request.form.get('additional_notes', '')
    )

    conn = get_db_connection()
    cur = conn.cursor()

    # Check if user already has a profile
    cur.execute("SELECT * FROM pregnancy_profile WHERE user_id = ?", (user_id,))
    existing_profile = cur.fetchone()

    if existing_profile:
        # Update existing profile
        cur.execute('''
            UPDATE pregnancy_profile 
            SET due_date=?, last_menstrual_period=?, previous_pregnancies=?, live_births=?, miscarriages=?, 
                current_week=?, doctor_name=?, doctor_contact=?, hospital_name=?, hospital_contact=?, blood_type=?, 
                allergies=?, medications=?, pre_existing_conditions=?, weight=?, height=?, diet=?, exercise=?, 
                smoking_status=?, alcohol_consumption=?, caffeine_intake=?, stress_levels=?, emotional_wellbeing=?, 
                partner_name=?, partner_contact=?, emergency_contact=?, birth_preferences=?, additional_notes=? 
            WHERE user_id=?
        ''', (*data, user_id))
    else:
        # Insert new profile
        cur.execute('''
            INSERT INTO pregnancy_profile 
            (user_id, due_date, last_menstrual_period, previous_pregnancies, live_births, miscarriages, current_week, 
            doctor_name, doctor_contact, hospital_name, hospital_contact, blood_type, allergies, medications, 
            pre_existing_conditions, weight, height, diet, exercise, smoking_status, alcohol_consumption, caffeine_intake, 
            stress_levels, emotional_wellbeing, partner_name, partner_contact, emergency_contact, birth_preferences, 
            additional_notes) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, *data))

    conn.commit()
    conn.close()
    
    return redirect('/profile1')

@app.route('/notifications')
def notifications():
    return render_template('notifications.html')

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM user_preferences WHERE user_id = ?', (session['user_id'],))
    preferences = cur.fetchone()
    conn.close()

    default_preferences = {
        'darkMode': False,
        'themeColor': 'blue',
        'showNsfw': False,
        'language': 'en'
    }

    user_preferences = dict(preferences) if preferences else default_preferences
    return render_template('settings.html', preferences=user_preferences)

@app.route('/save_preferences', methods=['POST'])
def save_preferences():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401

    try:
        preferences = request.get_json()
        conn = get_db_connection()
        cur = conn.cursor()

        # Convert boolean to integer for SQLite
        dark_mode = 1 if preferences.get('darkMode') else 0

        cur.execute('SELECT 1 FROM user_preferences WHERE user_id = ?', (session['user_id'],))
        exists = cur.fetchone()

        if exists:
            cur.execute('''
                UPDATE user_preferences 
                SET dark_mode = ?, theme_color = ?, show_nsfw = ?, language = ?
                WHERE user_id = ?
            ''', (dark_mode, preferences['themeColor'], preferences['showNsfw'], preferences['language'], session['user_id']))
        else:
            cur.execute('''
                INSERT INTO user_preferences (user_id, dark_mode, theme_color, show_nsfw, language)
                VALUES (?, ?, ?, ?, ?)
            ''', (session['user_id'], dark_mode, preferences['themeColor'], preferences['showNsfw'], preferences['language']))

        conn.commit()
        conn.close()

        # Update session
        session['preferences'] = {
            'darkMode': bool(dark_mode),
            'themeColor': preferences['themeColor'],
            'showNsfw': preferences['showNsfw'],
            'language': preferences['language']
        }

        return jsonify({'status': 'success', 'message': 'Preferences saved successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/change_language', methods=['POST'])
def change_language():
    data = request.get_json()
    language = data.get('language', 'en')
    session['language'] = language
    return jsonify({'status': 'success'})

@app.before_request
def before_request():
    if 'user_id' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM user_preferences WHERE user_id = ?', (session['user_id'],))
        preferences = cur.fetchone()
        conn.close()

        if preferences:
            g.theme_color = preferences['theme_color']
            g.dark_mode = preferences['dark_mode']
            g.language = preferences['language']
        else:
            g.theme_color = 'blue'
            g.dark_mode = False
            g.language = 'en'
    else:
        g.theme_color = 'blue'
        g.dark_mode = False
        g.language = 'en'

@app.context_processor
def inject_preferences():
    return {
        'theme_color': getattr(g, 'theme_color', 'blue'),
        'dark_mode': getattr(g, 'dark_mode', False),
        'current_language': getattr(g, 'language', 'en')
    }

# Run the App
if __name__ == '__main__':
    app.run(debug=True)