# Sounds API - Backend System

## 📖 Overview

Sounds API is a comprehensive backend system built with Flask that powers an educational platform focused on language learning and pronunciation improvement. The system supports multi-role users (admins and clients), level-based content management, video lessons, exam systems, and detailed progress tracking.

## ✨ Features

- **Multi-language Support**: Full Arabic and English localization
- **User Management**: Registration, authentication, and role-based access control
- **Level System**: Structured learning levels with videos and exams
- **Video Management**: YouTube integration with progress tracking
- **Question System**: Interactive questions with answer validation
- **Exam System**: Initial and final exams with score tracking
- **Progress Reporting**: Detailed user progress reports in multiple formats
- **Admin Dashboard**: Comprehensive administration tools
- **File Upload**: Secure image upload for level covers

## 🛠 Technology Stack

- **Backend Framework**: Flask
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL support
- **Authentication**: JWT tokens with Flask-JWT-Extended
- **Security**: Bcrypt for password hashing
- **Localization**: Custom multi-language support (English/Arabic)
- **File Handling**: Secure file uploads with UUID renaming
- **Validation**: Comprehensive input validation system

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/mahmoodhamdi/sounds_api.git
cd sounds_api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
export SECRET_KEY='your-secret-key'
export JWT_SECRET_KEY='your-jwt-secret'
export DATABASE_URL='sqlite:///site.db'  # or your PostgreSQL URL
```

5. Initialize the database:
```bash
python app.py
```

## 🚀 Usage

Start the development server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## 📚 API Documentation

### Authentication Endpoints
- `POST /register` - User registration
- `POST /login` - User login (supports Google login)

### User Management
- `GET /users/<id>` - Get user profile
- `PATCH /users/<id>` - Update user information
- `GET /admin/users` - Get all users (admin only)
- `DELETE /admin/users/<id>` - Delete user (admin only)

### Level Management
- `GET /levels` - Get all available levels
- `POST /levels` - Create new level (admin only)
- `PUT /levels/<id>` - Update level (admin only)
- `DELETE /levels/<id>` - Delete level (admin only)

### Video & Question System
- `POST /levels/<id>/videos` - Add video to level
- `POST /videos/<id>/questions` - Add question to video
- `POST /questions/<id>/submit` - Submit question answer

### Exam System
- `POST /exams/<level_id>/initial` - Submit initial exam
- `POST /exams/<level_id>/final` - Submit final exam

### Progress Tracking
- `GET /report` - Get user progress report (markdown/JSON)
- `GET /users/<id>/levels` - Get user's purchased levels

## 🔐 Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_token>
```

## 🌐 Localization

The API supports English (en) and Arabic (ar) languages. Specify language using:
- Query parameter: `?lang=ar`
- Form data: `lang=ar`
- Header: `Accept-Language: ar`

## 📊 Database Schema

Key models include:
- **User**: User accounts with roles
- **Level**: Learning levels with pricing
- **Video**: YouTube videos with questions
- **Question**: Interactive questions
- **UserLevel**: User progress per level
- **ExamResult**: Exam scores and results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is proprietary and confidential. All rights reserved.

## 👨‍💻 Developer

**Mahmood Hamdi**
- Email: hmdy7486@gmail.com
- WhatsApp: +201019793768
- GitHub: [mahmoodhamdi](https://github.com/mahmoodhamdi/)

## 🆘 Support

For technical support or questions, please contact the developer directly via email or WhatsApp.
