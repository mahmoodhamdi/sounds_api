# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sounds API is a Flask-based backend for an educational platform focused on language learning and pronunciation improvement. It provides a RESTful API with JWT authentication, role-based access control (admin/client), and multi-language support (English/Arabic).

## Commands

### Run Development Server
```bash
python app.py
```
Server starts at `http://localhost:5000` with debug mode enabled.

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Variables
```bash
export SECRET_KEY='your-secret-key'
export JWT_SECRET_KEY='your-jwt-secret'
export DATABASE_URL='postgresql://user:pass@localhost:5432/db'  # Optional, defaults to PostgreSQL
```

## Architecture

### Module Structure

| Module | Purpose |
|--------|---------|
| `app/__init__.py` | Flask app factory with `create_app()`, initializes DB/JWT/Bcrypt/CORS |
| `app/routes.py` | All 45 API endpoint handlers |
| `app/models.py` | 9 SQLAlchemy ORM models |
| `app/auth.py` | `@admin_required` and `@client_required` decorators, token creation |
| `app/localization.py` | `LocalizationHelper` class with 80+ bilingual message keys |
| `app/validation.py` | `ValidationHelper` class for input validation |
| `app/config.py` | Configuration class (database, JWT, upload paths) |

### Database Models

Core relationships:
- **User** → UserLevel (purchased levels) → UserVideoProgress (video completion)
- **Level** → Video → Question
- **User** → UserQuestionAnswer (answer submissions with pronunciation scores)
- **User** → ExamResult (initial/final exam scores)

### Authentication Flow

1. User registers/logs in via `/register` or `/login`
2. Server returns JWT token (24-hour expiration)
3. Client includes `Authorization: Bearer <token>` header
4. Route decorators (`@admin_required`, `@client_required`) enforce access control

### Localization System

Language is determined from (in order): query param `?lang=ar`, form data `lang`, or `Accept-Language` header. Default is English.

Access messages via:
```python
from app.localization import LocalizationHelper
message = LocalizationHelper.get_message('user_created', lang)
```

### File Uploads

- Level covers: `Uploads/levels/` (served at `/Uploads/levels/<filename>`)
- Profile pictures: `Uploads/profiles/` (served at `/Uploads/profiles/<filename>`)
- Files are renamed with UUID for security using `werkzeug.utils.secure_filename`

## API Route Categories

- **Auth**: `/register`, `/login`
- **Users**: `/users/<id>`, `/admin/users`
- **Levels**: `/levels`, `/levels/<id>`, `/admin/levels`
- **Videos**: `/levels/<id>/videos`, `/videos/<id>`, `/admin/videos`
- **Questions**: `/videos/<id>/questions`, `/questions/<id>`, `/questions/<id>/submit`
- **Exams**: `/exams/<level_id>/initial`, `/exams/<level_id>/final`
- **Progress**: `/report`, `/users/<id>/levels`

See `API_Documentation.md` for full endpoint specifications and `curl_commands.txt` for usage examples.

## Key Patterns

### Adding New Routes
Routes are defined in `app/routes.py` using the `bp` blueprint. Use existing decorators for auth:
```python
@bp.route('/new-endpoint', methods=['POST'])
@jwt_required()
@client_required
def new_endpoint():
    lang = get_language()
    # Implementation
```

### Adding New Localized Messages
Add entries to both `messages_en` and `messages_ar` dicts in `app/localization.py`.

### Input Validation
Use `ValidationHelper` methods: `is_valid_email()`, `is_valid_password()`, `is_numeric()`, `detect_language()`.
