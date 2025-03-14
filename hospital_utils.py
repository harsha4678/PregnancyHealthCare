import os
import smtplib
from datetime import datetime, timedelta

import googlemaps
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from requests.exceptions import RequestException

# Load environment variables from .env file
load_dotenv()

# Get the API key and email credentials from the .env file
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

gmaps_client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
geolocator = Nominatim(user_agent="hospital_locator")

# Mock database for storing appointments
appointments = []

# Specialty keywords dictionary
SPECIALTY_KEYWORDS = {
    "General Physical": [
        "normal, general, physical, checkup",
        "general checkup",
        "consult",
    ],
    "neurologist": [
        "neurologist",
        "neuro",
        "nerves",
        "brain doctor",
        "nerve specialist",
    ],
    "dermatologist": [
        "dermatologist",
        "derma",
        "skin",
        "skin specialist",
        "skin doctor",
    ],
    "cardiologist": ["cardiologist", "cardio", "heart doctor", "heart specialist"],
    "orthopedist": [
        "orthopedist",
        "orthopedic",
        "bone doctor",
        "joint specialist",
        "orthopedics",
    ],
    "pediatrician": [
        "pediatrician",
        "child doctor",
        "pediatrics",
        "children specialist",
    ],
    "gynecologist": ["gynecologist", "gyno", "obstetrician", "obgyn", "women's doctor"],
    "psychiatrist": [
        "psychiatrist",
        "mental health",
        "psych doctor",
        "mind specialist",
    ],
    "dentist": ["dentist", "dental", "teeth doctor", "oral care", "tooth specialist"],
    "oncologist": ["oncologist", "cancer specialist", "cancer doctor", "oncology"],
    "endocrinologist": ["endocrinologist", "hormone specialist", "gland doctor"],
    "ophthalmologist": [
        "ophthalmologist",
        "eye doctor",
        "vision specialist",
        "eye care",
    ],
    "urologist": ["urologist", "urinary specialist", "kidney doctor", "urinary care"],
    "gastroenterologist": [
        "gastroenterologist",
        "gastro",
        "stomach doctor",
        "digestive care",
    ],
    "pulmonologist": ["pulmonologist", "lung doctor", "respiratory specialist"],
    "ent": ["ENT", "ear nose throat", "ENT specialist", "otolaryngologist"],
    "rheumatologist": [
        "rheumatologist",
        "arthritis specialist",
        "joint care",
        "autoimmune specialist",
    ],
    "radiologist": ["radiologist", "imaging specialist", "radiology"],
    "nephrologist": ["nephrologist", "kidney doctor", "renal specialist"],
    "allergist": ["allergist", "immunologist", "allergy specialist", "immune care"],
    "surgeon": ["surgeon", "surgery specialist", "operation doctor"],
}


def get_hospitals(
    location=None, latitude=None, longitude=None, specialization="hospital"
):
    """
    Fetch nearby hospitals based on location or GPS coordinates and specialization.
    """
    try:
        # Validate specialization
        keywords = SPECIALTY_KEYWORDS.get(specialization.lower(), ["hospital"])

        if location:
            # Use Google Maps API for geocoding
            try:
                geocode_result = gmaps_client.geocode(location)  # type: ignore
                if not geocode_result:
                    return {"error": "Invalid location provided."}
                lat = geocode_result[0]["geometry"]["location"]["lat"]
                lng = geocode_result[0]["geometry"]["location"]["lng"]
            except RequestException as e:
                return {"error": f"Failed to resolve location: {str(e)}"}
            except Exception as e:
                return {"error": f"Geocoding error: {str(e)}"}
        elif latitude and longitude:
            # Use provided latitude and longitude
            lat, lng = latitude, longitude
        else:
            return {"error": "Either location or GPS coordinates are required."}

        all_hospitals = []

        # Search using each keyword
        for keyword in keywords:
            places_result = gmaps_client.places(  # type: ignore
                query=keyword, location=(lat, lng), radius=5000, type="hospital"
            )
            # Add hospitals to the result list
            for place in places_result.get("results", []):
                all_hospitals.append(
                    {
                        "name": place["name"],
                        "address": place.get("vicinity", ""),
                        "rating": place.get("rating", "N/A"),
                        "user_ratings_total": place.get("user_ratings_total", 0),
                    }
                )

        # Remove duplicates by converting the list of dictionaries to a set and back
        unique_hospitals = [dict(t) for t in {tuple(d.items()) for d in all_hospitals}]
        return {"hospitals": unique_hospitals}

    except Exception as e:
        return {"error": str(e)}


def book_appointment(hospital_name, user_name, user_email, slot):
    """
    Book an appointment and send confirmation email.
    """
    if not all([hospital_name, user_name, user_email, slot]):
        return {"error": "Hospital name, user name, user email, and slot are required."}

    try:
        # Save appointment in mock database
        appointment = {
            "user_name": user_name,
            "user_email": user_email,
            "hospital_name": hospital_name,
            "slot": slot,
            "reminders_sent": False,
        }
        appointments.append(appointment)

        # Send confirmation email
        send_email(
            to_email=user_email,
            subject="Appointment Confirmation",
            body=f"Hi {user_name},\n\nYour appointment at {hospital_name} has been confirmed for {slot}.\n\nThank you!",
        )

        return {"message": "Appointment booked successfully!"}

    except Exception as e:
        return {"error": str(e)}


def send_email(to_email, subject, body):
    """
    Utility function to send an email.
    """
    try:
        if SENDER_EMAIL is None or SENDER_PASSWORD is None:
            print("Email credentials not available. Check environment variables.")
            return

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            email_message = f"Subject: {subject}\n\n{body}"
            server.sendmail(SENDER_EMAIL, to_email, email_message)
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_reminders():
    """
    Send appointment reminders 15-120 minutes before the appointment.
    """
    now = datetime.now()
    for appointment in appointments:
        if appointment["reminders_sent"]:
            continue

        slot_time = datetime.strptime(appointment["slot"], "%Y-%m-%d %H:%M")
        time_diff = slot_time - now

        if timedelta(minutes=15) <= time_diff <= timedelta(minutes=120):
            # Send reminder email
            send_email(
                to_email=appointment["user_email"],
                subject="Appointment Reminder",
                body=f"Hi {appointment['user_name']},\n\nThis is a reminder for your appointment at {appointment['hospital_name']} scheduled for {appointment['slot']}.\n\nThank you!",
            )
            appointment["reminders_sent"] = True

import json
import os
import random
from typing import Any, Dict, List, Optional

# Try to import googlemaps for actual API calls
try:
    import googlemaps

    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False
    print("Warning: googlemaps library not found. Using mock hospital data.")

# Get API key from environment
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")

# Initialize Google Maps client if API key is available
gmaps_client = None
if GOOGLE_MAPS_API_KEY and GOOGLEMAPS_AVAILABLE:
    try:
        gmaps_client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
    except Exception as e:
        print(f"Error initializing Google Maps client: {str(e)}")

# Mock hospital data for testing or when API is unavailable
MOCK_HOSPITALS = [
    {
        "name": "City General Hospital",
        "address": "123 Main St, City Center",
        "rating": 4.5,
        "specializations": [
            "General Physical",
            "Gynecologist",
            "Pediatrician",
            "Cardiologist",
        ],
        "phone": "+1-555-123-4567",
    },
    {
        "name": "Women's Health Center",
        "address": "456 Oak Ave, Westside",
        "rating": 4.8,
        "specializations": ["Gynecologist", "Pediatrician"],
        "phone": "+1-555-987-6543",
    },
    {
        "name": "Family Care Medical",
        "address": "789 Pine Rd, Eastside",
        "rating": 4.2,
        "specializations": ["General Physical", "Pediatrician", "Dermatologist"],
        "phone": "+1-555-456-7890",
    },
    {
        "name": "Comprehensive Medical Center",
        "address": "101 Cedar Blvd, Northside",
        "rating": 4.6,
        "specializations": [
            "Gynecologist",
            "Neurologist",
            "Cardiologist",
            "Orthopedist",
        ],
        "phone": "+1-555-789-0123",
    },
    {
        "name": "Community Health Services",
        "address": "202 Elm St, Southside",
        "rating": 4.0,
        "specializations": ["General Physical", "Gynecologist", "Psychiatrist"],
        "phone": "+1-555-321-6540",
    },
]


def get_hospitals(
    location: str, specialization: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get hospitals near a location with optional specialization filter.
    Falls back to mock data if the Google Maps API is not available.

    Args:
        location: City or address to search near
        specialization: Optional medical specialization to filter by

    Returns:
        Dict with hospitals and status information
    """
    try:
        # Try to use Google Maps API if available
        if gmaps_client:
            # Query for places with the 'hospital' type near the provided location
            places_result = gmaps_client.places_nearby(  # type: ignore
                location=location,
                keyword=f"hospital {specialization}" if specialization else "hospital",
                radius=5000,  # 5km radius
                type="hospital",
            )

            # Extract relevant hospital data
            hospitals = []
            for place in places_result.get("results", []):
                hospital = {
                    "name": place.get("name", "Unknown"),
                    "address": place.get("vicinity", "No address available"),
                    "rating": place.get("rating", "No rating"),
                    "specializations": (
                        [specialization] if specialization else ["General"]
                    ),
                    "place_id": place.get("place_id", ""),
                }
                hospitals.append(hospital)

            return {
                "status": "success",
                "hospitals": hospitals,
                "count": len(hospitals),
                "source": "Google Maps API",
            }
        else:
            # Fall back to mock data if API is not available
            filtered_hospitals = MOCK_HOSPITALS

            # Filter by specialization if provided
            if specialization:
                filtered_hospitals = [
                    h
                    for h in MOCK_HOSPITALS
                    if specialization in h.get("specializations", [])
                ]

            # Simulate location-based filtering (just randomize for mock data)
            random.shuffle(filtered_hospitals)
            # Limit to 3-5 random results for realistic mock data
            result_count = random.randint(3, min(5, len(filtered_hospitals)))
            filtered_hospitals = filtered_hospitals[:result_count]

            return {
                "status": "success",
                "hospitals": filtered_hospitals,
                "count": len(filtered_hospitals),
                "source": "Mock Data",
            }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Error fetching hospital data: {str(e)}",
            "hospitals": [],
            "count": 0,
        }


# For testing purposes
if __name__ == "__main__":
    # Test with a sample location
    result = get_hospitals("New York", "Gynecologist")
    print(json.dumps(result, indent=2))
