# Safe Travel Companion

A secure platform for university students to find travel companions within their institution.

## Tech Stack

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript
- Database: Sqlite

## Setup Instructions

### Backend Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
cd server
pip install -r requirements.txt
```

3. Set up Sqlite:
- Create a new Sqlite database named 'safe_travel.db'
- Update the DATABASE_URL in `.env` with your Sqlite credentials

4. Configure environment variables:
- Update `.env` file with your:
  - Google OAuth credentials
  - Email server settings
  - Secret key

5. Initialize the database:
```bash
python app.py
```

### Frontend Setup

1. Configure Google OAuth:
- Update the Google Client ID in `client/index.html`
- Update the Font Awesome kit URL in `client/index.html`

2. Serve the frontend:
- Use any static file server (e.g., Python's http.server)
```bash
cd client
python -m http.server 3000
```

## Usage

1. Access the application:
- Backend: http://localhost:5000
- Frontend: http://localhost:3000

2. Register with your university email (g.bracu.ac.bd)
3. Verify your email address
4. Set up your profile and class schedule

## Security Features

- Email domain restriction (g.bracu.ac.bd only)
- Password hashing
- Input validation
