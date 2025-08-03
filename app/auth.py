from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.models import User
from app import bcrypt
from app.localization import LocalizationHelper
from app.validation import ValidationHelper

def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            lang = ValidationHelper.get_language_from_request()
            return LocalizationHelper.get_error_response('admin_access_required', lang, 403)
        return f(*args, **kwargs)
    return decorated_function

def client_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            lang = ValidationHelper.get_language_from_request()
            return LocalizationHelper.get_error_response('authentication_required', lang, 401)
        return f(*args, **kwargs)
    return decorated_function

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return user
    return None

def create_user_token(user):
    return create_access_token(identity=str(user.id))