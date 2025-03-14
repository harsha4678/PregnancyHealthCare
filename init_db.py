import os
import sqlite3

# Create database directory if it doesn't exist
DB_FILE = "pregnancy.db"


def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Create users table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    )

    # Create pregnancy_profile table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS pregnancy_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        due_date TEXT,
        last_menstrual_period TEXT,
        previous_pregnancies INTEGER DEFAULT 0,
        live_births INTEGER DEFAULT 0,
        miscarriages INTEGER DEFAULT 0,
        current_week INTEGER DEFAULT 0,
        doctor_name TEXT,
        doctor_contact TEXT,
        hospital_name TEXT,
        hospital_contact TEXT,
        blood_type TEXT,
        allergies TEXT,
        medications TEXT,
        pre_existing_conditions TEXT,
        weight REAL,
        height REAL,
        diet TEXT,
        exercise TEXT,
        smoking_status TEXT,
        alcohol_consumption TEXT,
        caffeine_intake TEXT,
        stress_levels TEXT,
        emotional_wellbeing TEXT,
        partner_name TEXT,
        partner_contact TEXT,
        emergency_contact TEXT,
        birth_preferences TEXT,
        additional_notes TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """
    )

    # Create health_records table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS health_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        file_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """
    )

    # Create symptoms table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS symptoms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symptom TEXT NOT NULL,
        advice TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """
    )

    # Create appointments table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        hospital_name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        status TEXT DEFAULT 'Scheduled',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """
    )

    # Create user_preferences table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS user_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        dark_mode INTEGER DEFAULT 0,
        theme_color TEXT DEFAULT 'blue',
        show_nsfw INTEGER DEFAULT 0,
        language TEXT DEFAULT 'en',
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """
    )

    # Create pregnancy_records table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS pregnancy_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date_type TEXT NOT NULL,
        input_date TEXT NOT NULL,
        calculated_due_date TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """
    )

    # Create exercises table
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        image TEXT NOT NULL,
        reps TEXT NOT NULL,
        description TEXT,
        trimester TEXT,
        difficulty TEXT DEFAULT 'Medium'
    )
    """
    )

    # Insert some example exercises
    exercises = [
        (
            "Pelvic Tilt",
            "pelvic_tilt.jpg",
            "10-15 repetitions",
            "Helps with lower back pain",
            "All",
            "Easy",
        ),
        (
            "Kegel Exercises",
            "kegel.jpg",
            "10 repetitions, hold for 5-10 seconds each",
            "Strengthens pelvic floor",
            "All",
            "Easy",
        ),
        (
            "Wall Slide",
            "wall_slide.jpg",
            "10-12 repetitions",
            "Improves posture",
            "First,Second",
            "Medium",
        ),
        (
            "Side-Lying Leg Lift",
            "side_leg_lift.jpg",
            "10 repetitions each side",
            "Strengthens hips and core",
            "Second,Third",
            "Medium",
        ),
        (
            "Seated Twist",
            "seated_twist.jpg",
            "5 repetitions each side",
            "Relieves back tension",
            "First,Second",
            "Easy",
        ),
    ]

    # Check if exercises table is empty before inserting
    cur.execute("SELECT COUNT(*) FROM exercises")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO exercises (name, image, reps, description, trimester, difficulty) VALUES (?, ?, ?, ?, ?, ?)",
            exercises,
        )

    conn.commit()
    conn.close()

    print(f"Database {DB_FILE} initialized successfully.")


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Done.")
