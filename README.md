# Pregnancy Healthcare App

A comprehensive web application to support pregnant women with healthcare information, symptom checking, appointment scheduling, and more.

## Features

- **Symptom Checker**: AI-powered chat interface for pregnancy-related symptom inquiry
- **Diet Plan Generator**: Personalized nutrition recommendations based on trimester, health conditions, and preferences
- **Appointment Booking**: Schedule appointments with healthcare providers
- **Health Record Management**: Upload and store medical documents
- **Pregnancy Tracker**: Track baby's growth, calculate due date, and receive week-specific information
- **Exercise Recommendations**: Pregnancy-safe exercise routines
- **Weight Gain Calculator**: Track healthy weight gain based on BMI and pregnancy stage
- **User Profile**: Store pregnancy-related health information

## Tech Stack

- **Backend**: Python with Flask framework
- **Database**: SQLite for data persistence
- **AI Integration**: Google Generative AI (Gemini) for symptom analysis
- **Frontend**: HTML, CSS, JavaScript
- **APIs**: Google Maps for hospital search

## Installation

1. **Clone the repository**
   ```
   git clone <repository-url>
   cd PregnancyHealthCare
   ```

2. **Set up a virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Create environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your API keys and configuration values

5. **Initialize the database**
   ```
   python init_db.py
   ```

6. **Run the application**
   ```
   python app.py
   ```

## Configuration

The application uses the following environment variables:

- `GEMINI_API_KEY`: Google Generative AI API key for the symptom checker
- `GOOGLE_MAPS_API_KEY`: API key for hospital location search
- `CONTEXT_AWARENESS`: Boolean flag to enable AI chat context memory (default: false)
- `SENDER_EMAIL`: Email for notifications (optional)
- `SENDER_PASSWORD`: Password for the email account (optional)

## Usage

1. Register an account or login
2. Navigate through the dashboard to access different features
3. Use the symptom checker for pregnancy-related concerns
4. Generate personalized diet plans
5. Book appointments with healthcare providers
6. Track your pregnancy and baby's development

## License

This project is licensed under the MIT License - see the LICENSE file for details.
