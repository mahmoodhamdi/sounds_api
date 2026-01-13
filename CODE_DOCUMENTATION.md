# Sounds API - Code Documentation
# توثيق الكود

---

## Table of Contents
1. [Project Structure](#project-structure)
2. [Entry Point](#entry-point)
3. [Application Factory](#application-factory)
4. [Configuration](#configuration)
5. [Database Models](#database-models)
6. [Authentication System](#authentication-system)
7. [Localization System](#localization-system)
8. [Validation System](#validation-system)
9. [Routes Documentation](#routes-documentation)
10. [Helper Functions](#helper-functions)

---

## 1. Project Structure

```
sounds_api/
├── app.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── swagger.yaml              # OpenAPI 3.0 specification
├── CLAUDE.md                 # AI assistant guidelines
├── PROJECT_ASSESSMENT.md     # Full project assessment
├── CODE_DOCUMENTATION.md     # This file
├── API_Documentation.md      # API endpoint documentation
├── curl_commands.txt         # Example API calls
├── Uploads/                  # User uploaded files
│   ├── levels/              # Level cover images
│   └── profiles/            # User profile pictures
└── app/                      # Main application package
    ├── __init__.py          # Flask app factory
    ├── config.py            # Configuration settings
    ├── models.py            # SQLAlchemy ORM models
    ├── routes.py            # API route handlers
    ├── auth.py              # Authentication decorators
    ├── localization.py      # Multi-language support
    ├── validation.py        # Input validation helpers
    └── swagger.py           # Swagger UI integration
```

---

## 2. Entry Point

### `app.py`

```python
from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(host='0.0.0.0', port=5000, debug=True)
```

**What it does:**
- Creates Flask application using factory pattern
- Initializes database tables on startup
- Runs development server on all interfaces (0.0.0.0)

**Production Note:** Replace with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## 3. Application Factory

### `app/__init__.py`

```python
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    CORS(app)           # Enable Cross-Origin requests
    db.init_app(app)    # Initialize SQLAlchemy
    bcrypt.init_app(app) # Initialize password hashing
    jwt.init_app(app)   # Initialize JWT authentication

    from app import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        db.create_all()

    return app
```

**Components Initialized:**
| Component | Library | Purpose |
|-----------|---------|---------|
| `db` | Flask-SQLAlchemy | Database ORM |
| `bcrypt` | Flask-Bcrypt | Password hashing |
| `jwt` | Flask-JWT-Extended | Token authentication |
| `CORS` | Flask-CORS | Cross-origin support |

---

## 4. Configuration

### `app/config.py`

```python
class Config:
    # Security Keys
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt_secret_key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'postgresql://user:pass@localhost:5432/db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Uploads
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Uploads', 'levels')
    PROFILE_UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Uploads', 'profiles')
    MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
```

**Environment Variables Required:**
```bash
export SECRET_KEY='your-32-char-secret-key'
export JWT_SECRET_KEY='your-jwt-secret-key'
export DATABASE_URL='postgresql://user:pass@host:5432/dbname'
```

---

## 5. Database Models

### `app/models.py`

#### Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │────<│  UserLevel  │>────│    Level    │
└─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │
      │                   │                   │
      ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ ExamResult  │     │UserVideoProg│     │    Video    │
└─────────────┘     └─────────────┘     └─────────────┘
      │                                       │
      │                                       │
      ▼                                       ▼
┌─────────────┐                         ┌─────────────┐
│UserQuestion │<────────────────────────│  Question   │
│   Answer    │                         └─────────────┘
└─────────────┘
```

#### Model Details

##### WelcomeVideo
```python
class WelcomeVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_url = db.Column(db.String(200), nullable=False)
```
- **Purpose:** Store global welcome video URL
- **Cardinality:** Single record (replaced on update)

##### User
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)  # Bcrypt hash
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default='client')  # 'admin' | 'client'
    picture = db.Column(db.String(200), nullable=True)
    levels = db.relationship('UserLevel', backref='user', lazy=True)
```
- **Roles:** `admin` (full access), `client` (user access)
- **Password:** Bcrypt hashed, 60 characters

##### Level
```python
class Level(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    level_number = db.Column(db.Integer, nullable=False)
    welcome_video_url = db.Column(db.String(200), nullable=True)
    image_path = db.Column(db.String(200), nullable=True)
    price = db.Column(db.Float, nullable=False)
    initial_exam_question = db.Column(db.Text, nullable=True)
    final_exam_question = db.Column(db.Text, nullable=True)
    videos = db.relationship('Video', backref='level', lazy=True)
    user_levels = db.relationship('UserLevel', backref='level', lazy=True)
```

##### Video
```python
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    youtube_link = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=1)
    questions = db.relationship('Question', backref='video', lazy=True,
                               cascade='all, delete-orphan')
```
- **cascade='all, delete-orphan':** Deleting video deletes its questions

##### Question
```python
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_answers = db.relationship('UserQuestionAnswer', backref='question',
                                   lazy=True, cascade='all, delete-orphan')
```

##### UserLevel (Association Table)
```python
class UserLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    can_take_final_exam = db.Column(db.Boolean, default=False)
    initial_exam_score = db.Column(db.Float, nullable=True)
    final_exam_score = db.Column(db.Float, nullable=True)
    score_difference = db.Column(db.Float, nullable=True)
    videos_progress = db.relationship('UserVideoProgress', backref='user_level')
```
- **Purpose:** Track user's purchased levels and progress

##### UserVideoProgress
```python
class UserVideoProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_level_id = db.Column(db.Integer, db.ForeignKey('user_level.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    is_opened = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)
```
- **is_opened:** Video is unlocked for viewing
- **is_completed:** User finished watching

##### UserQuestionAnswer
```python
class UserQuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    speechace_response = db.Column(db.Text, nullable=True)  # JSON string
    percentage = db.Column(db.Float, nullable=False, default=0.0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
```

##### ExamResult
```python
class ExamResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    speechace_response = db.Column(db.Text, nullable=True)  # JSON string
    percentage = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'initial' | 'final'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 6. Authentication System

### `app/auth.py`

#### Decorators

##### @admin_required
```python
@admin_required
def admin_only_route():
    # Only users with role='admin' can access
    pass
```

**Flow:**
1. Check JWT token validity
2. Get user from database
3. Verify user.role == 'admin'
4. Return 403 if not admin

##### @client_required
```python
@client_required
def authenticated_route():
    # Any authenticated user (admin or client) can access
    pass
```

**Flow:**
1. Check JWT token validity
2. Get user from database
3. Return 401 if user not found

#### Helper Functions

##### authenticate_user(email, password)
```python
def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return user
    return None
```

##### create_user_token(user)
```python
def create_user_token(user):
    return create_access_token(identity=str(user.id))
```
- Returns JWT token with 24-hour expiration
- Identity is user.id as string

---

## 7. Localization System

### `app/localization.py`

#### LocalizationHelper Class

```python
class LocalizationHelper:
    MESSAGES = {
        'en': {
            'user_not_found': 'User not found',
            # ... 40+ message keys
        },
        'ar': {
            'user_not_found': 'المستخدم غير موجود',
            # ... 40+ message keys
        }
    }
```

#### Methods

##### get_message(key, lang='en', **kwargs)
```python
message = LocalizationHelper.get_message('required_field', 'ar', field='Email')
# Returns: 'Email مطلوب'
```

##### get_error_response(key, lang, status_code, **kwargs)
```python
return LocalizationHelper.get_error_response('user_not_found', 'en', 404)
# Returns: ({'success': False, 'message': 'User not found', ...}, 404)
```

##### get_success_response(key, data, lang, **kwargs)
```python
return LocalizationHelper.get_success_response(
    'user_created_successfully',
    {'id': 1, 'name': 'John'},
    'en'
)
# Returns: ({'success': True, 'message': '...', 'id': 1, 'name': 'John'}, 200)
```

#### Adding New Messages

```python
MESSAGES = {
    'en': {
        'new_message_key': 'Your message in English with {variable}',
    },
    'ar': {
        'new_message_key': 'رسالتك بالعربي مع {variable}',
    }
}
```

---

## 8. Validation System

### `app/validation.py`

#### ValidationHelper Class

##### get_language_from_request()
```python
lang = ValidationHelper.get_language_from_request()
```
**Priority:**
1. `?lang=ar` query parameter
2. `lang` in form data
3. `lang` in JSON body
4. `Accept-Language` header
5. Default: `'en'`

##### validate_email(email)
```python
if not ValidationHelper.validate_email(email):
    return error_response
```
**Pattern:** `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

##### validate_password(password)
```python
if not ValidationHelper.validate_password(password):
    return error_response
```
**Rule:** Minimum 6 characters

##### validate_required_fields(data, required_fields, lang)
```python
errors = ValidationHelper.validate_required_fields(
    data,
    ['name', 'email', 'password'],
    lang
)
if errors:
    return {'errors': errors}, 400
```

##### validate_numeric_field(value, field_name, lang)
```python
error = ValidationHelper.validate_numeric_field(price, 'Price', lang)
if error:
    return {'message': error}, 400
```

##### sanitize_string(value, max_length=None)
```python
safe_input = ValidationHelper.sanitize_string(user_input, max_length=100)
```

---

## 9. Routes Documentation

### `app/routes.py`

#### Blueprint Registration
```python
bp = Blueprint("main", __name__)
```

#### Route Categories

| Category | Endpoints Count | Auth Required |
|----------|----------------|---------------|
| Welcome Video | 2 | POST: Admin, GET: None |
| Authentication | 2 | None |
| User Management | 7 | Yes |
| Level Management | 6 | Mixed |
| Video Management | 5 | Admin |
| Question Management | 6 | Admin/Client |
| Exams | 3 | Client |
| Progress | 5 | Client |
| Statistics | 2 | Admin |
| Static Files | 2 | None |

#### Common Patterns

##### Getting Language
```python
@bp.route("/example", methods=["GET"])
def example():
    lang = ValidationHelper.get_language_from_request()
    # Use lang for responses
```

##### Getting Current User
```python
@bp.route("/example", methods=["GET"])
@client_required
def example():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
```

##### Access Control Pattern
```python
@bp.route("/resource/<int:id>", methods=["GET"])
@client_required
def get_resource(id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    # Admin can access any, client only their own
    if user.role != "admin" and current_user_id != id:
        return LocalizationHelper.get_error_response("access_denied", lang, 403)
```

##### File Upload Pattern
```python
if "file" in request.files:
    file = request.files["file"]
    if file and file.filename != "":
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            unique_filename
        )
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        model.image_path = f"/Uploads/levels/{unique_filename}"
```

---

## 10. Helper Functions

### In `app/routes.py`

#### handle_profile_picture_upload(file)
```python
def handle_profile_picture_upload(file):
    """
    Handle profile picture file upload.

    Args:
        file: FileStorage object from request.files

    Returns:
        str: URL path like '/Uploads/profiles/uuid_filename.jpg'
        None: If upload failed or invalid file
    """
```
**Allowed Extensions:** png, jpg, jpeg, gif, webp

#### _format_video_data(video)
```python
def _format_video_data(video):
    """
    Format video object for API response.

    Args:
        video: Video model instance

    Returns:
        dict: {id, name, order, youtube_link, questions: [...]}
    """
```

#### extract_pronunciation_score(speechace_response)
```python
def extract_pronunciation_score(speechace_response):
    """
    Extract pronunciation score from SpeechAce API response.

    Args:
        speechace_response: dict from SpeechAce API

    Returns:
        float: Pronunciation score (0.0 to 100.0)

    Expected Structure:
        {
            'text_score': {
                'speechace_score': {
                    'pronunciation': 85.5
                }
            }
        }
    """
```

---

## Appendix: Quick Reference

### HTTP Status Codes Used

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST (new resource) |
| 400 | Bad Request | Validation error, missing fields |
| 401 | Unauthorized | Invalid/missing JWT token |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Database error, file error |

### Response Format

All responses follow this structure:
```json
{
    "success": true,
    "message": "Human readable message",
    "message_key": "localization_key",
    "lang": "en",
    // Additional data fields...
}
```

### JWT Token Usage

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Token expiration: 24 hours

---

*Documentation generated for Sounds API v1.0*
*Last updated: 2026-01-13*
