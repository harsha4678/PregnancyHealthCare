# Project Architecture

## System Overview

The Pregnancy Healthcare App is built on a Flask-based web application with a SQLite database. The system follows a traditional web application architecture with server-side rendering and some AJAX functionality for dynamic interactions.

```mermaid
flowchart TD
    A[Web Browser] <--> B[Flask Server]
    B <--> C[SQLite Database]
    B <--> D[External APIs]
    D -->|AI Responses| B
    D -->|Location Data| B
    
    subgraph "External Services"
        D[External APIs]
        E[Google Generative AI]
        F[Google Maps API]
    end
    
    D --- E
    D --- F
```

## Core Components

### 1. Backend (Flask Application)

The backend is organized as follows:

- **app.py**: Main application file containing routes and business logic
- **hospital_utils.py**: Utility functions for hospital search functionality
- **models**: Data models representing the database schema
- **templates**: HTML templates using Jinja2 for rendering views
- **static**: CSS, JavaScript, and static assets

```mermaid
classDiagram
    class FlaskApp {
        +routes()
        +config()
        +error_handlers()
    }
    
    class Utils {
        +get_hospitals()
        +get_db_connection()
    }
    
    class Database {
        +users
        +health_records
        +symptoms
        +appointments
    }
    
    class ExternalAPIs {
        +generate_ai_content()
        +search_hospitals()
    }
    
    FlaskApp --> Utils
    FlaskApp --> Database
    FlaskApp --> ExternalAPIs
```

### 2. Database (SQLite)

The database schema includes the following key tables:

- **users**: User account information
- **pregnancy_profile**: Detailed pregnancy-related user information
- **health_records**: References to uploaded health documents
- **symptoms**: Record of symptom checker interactions
- **appointments**: Scheduled medical appointments
- **user_preferences**: User interface and system preferences

```mermaid
erDiagram
    USERS ||--o{ PREGNANCY_PROFILE : has
    USERS ||--o{ HEALTH_RECORDS : uploads
    USERS ||--o{ SYMPTOMS : records
    USERS ||--o{ APPOINTMENTS : schedules
    USERS ||--o{ USER_PREFERENCES : configures

    USERS {
        int id PK
        string name
        string phone
        string password
    }

    PREGNANCY_PROFILE {
        int id PK
        int user_id FK
        date due_date
        date last_menstrual_period
        int current_week
    }

    HEALTH_RECORDS {
        int id PK
        int user_id FK
        string file_name
        string file_path
        datetime upload_date
    }

    SYMPTOMS {
        int id PK
        int user_id FK
        string symptom
        string advice
        datetime created_at
    }

    APPOINTMENTS {
        int id PK
        int user_id FK
        string hospital_name
        string specialization
        date date
        time time
        string status
    }

    USER_PREFERENCES {
        int id PK
        int user_id FK
        boolean dark_mode
        string theme_color
        string language
    }
```

### 3. External Integrations

- **Google Generative AI (Gemini)**: Provides AI capabilities for the symptom checker
- **Google Maps API**: Hospital and healthcare provider location services

## Key Workflows

### 1. Symptom Checker Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Server
    participant GeminiAI
    participant Database

    User->>Browser: Enter symptom question
    Browser->>Server: POST /chat
    
    alt Context Awareness Enabled
        Server->>Server: Retrieve conversation history
        Server->>GeminiAI: Send prompt with context
    else Context Awareness Disabled
        Server->>GeminiAI: Send prompt without context
    end
    
    GeminiAI->>Server: Return AI response
    Server->>Database: Save interaction
    Server->>Browser: Return response
    Browser->>User: Display response
```

### 2. Appointment Booking Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Server
    participant MapsAPI
    participant Database

    User->>Browser: Select specialty & location
    Browser->>Server: POST /book_appointment
    Server->>MapsAPI: Query nearby providers
    MapsAPI->>Server: Return provider list
    Server->>Browser: Display provider options
    
    User->>Browser: Select provider, date, time
    Browser->>Server: POST /book_appointment (confirm)
    Server->>Database: Save appointment
    Server->>Browser: Confirmation message
    Browser->>User: Display confirmation
```

### 3. Health Records Management

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Server
    participant FileSystem
    participant Database

    User->>Browser: Upload document
    Browser->>Server: POST /upload_record
    Server->>Server: Validate file
    Server->>Server: Secure filename
    Server->>FileSystem: Save file
    Server->>Database: Store reference
    Server->>Browser: Confirmation
    Browser->>User: Display success message
```

## Security Considerations

1. **Authentication**: Session-based user authentication
2. **Data Protection**:
   - Secure file handling with sanitized filenames
   - Environment variables for sensitive configuration
3. **Input Validation**: Form validation for user inputs
4. **API Security**: API keys stored in environment variables

## Scalability Considerations

The current architecture uses SQLite which is suitable for development but has limitations for production scale:

- **Database Migration Path**: Design allows for future migration to PostgreSQL or MySQL
- **Stateless Design**: Session management can be adapted for distributed deployment
- **API-First Approach**: Core functionality exposed through internal APIs, enabling future mobile app development

```mermaid
flowchart TD
    subgraph "Current Architecture"
        A[Web Browser] --> B[Single Flask Server]
        B --> C[SQLite Database]
    end

    subgraph "Future Scalable Architecture"
        D[Web Browser] --> E[Load Balancer]
        E --> F1[Flask Server 1]
        E --> F2[Flask Server 2]
        E --> F3[Flask Server 3]
        F1 --> G[PostgreSQL Database]
        F2 --> G
        F3 --> G
        H[Redis Cache] --- F1
        H --- F2
        H --- F3
    end
```
