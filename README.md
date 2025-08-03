# Educational Platform API

## Overview

This is a Flask-based API for an educational platform that manages users, levels, videos, questions, exams, and progress tracking. It supports JWT authentication, role-based access control (admin and client), file uploads, and multilingual responses (English and Arabic).

## Features

- User authentication (register, login, password reset)
- Role-based access control (admin and client)
- Level management (create, update, delete, purchase)
- Video and question management
- Exam submission and progress tracking
- User reports in JSON or Markdown format
- Admin statistics
- File uploads for level images
- Multilingual support (English and Arabic)

## Requirements

- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Flask-Bcrypt
- Flask-JWT-Extended
- Flask-CORS
- SQLite (default, configurable for other databases)

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables (optional):

   ```bash
   export SECRET_KEY='your_secret_key'
   export JWT_SECRET_KEY='jwt_secret_key'
   export DATABASE_URL='sqlite:///site.db'  # Or other database URI
   ```

5. Run the application:

   ```bash
   python app.py
   ```

## Project Structure

```
├── app/
│   ├── __init__.py      # Flask app initialization
│   ├── config.py        # Configuration settings
│   ├── auth.py          # Authentication logic
│   ├── localization.py   # Multilingual support
│   ├── models.py        # Database models
│   ├── validation.py    # Input validation
│   ├── routes.py        # API endpoints
├── app.py               # Main application entry point
├── Uploads/             # Directory for level images
├── tests/               # Test scripts (e.g., test.py)
├── requirements.txt     # Dependencies
├── API_Documentation.md # API documentation
├── README.md            # This file
```

## Running the Application

- The API runs on `http://localhost:5000` by default.
- Use `python app.py` to start the server in debug mode.

## Testing

Run the test suite to verify all endpoints:

```bash
python tests/test.py
```

## API Documentation

See `API_Documentation.md` for detailed endpoint descriptions, request/response formats, and error handling.

## Notes

- Ensure the `Uploads/levels` directory exists for file uploads.
- SQLite is used by default; configure `DATABASE_URL` for other databases.
- Admin routes require a user with `role: admin`.
- JWT tokens are required for protected routes.
