import os
from datetime import timedelta
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt_secret_key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # PostgreSQL Database with URL-encoded password
    password = quote_plus('F1@sk_P0stgr3s_2024!S3cur3')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'postgresql://soundread_user:{password}@localhost:5432/soundread_db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Uploads', 'levels')
    PROFILE_UPLOAD_FOLDER = os.path.join(os.getcwd(), 'Uploads', 'profiles')  # NEW
    MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB limit  # NEW    