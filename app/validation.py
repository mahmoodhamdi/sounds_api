import re
from flask import request

class ValidationHelper:
    """Helper class for input validation"""
    
    @staticmethod
    def get_language_from_request():
        """Extract language preference from request"""
        # Check for lang parameter in query string, form data, or headers
        lang = request.args.get('lang') or \
               request.form.get('lang') or \
               request.headers.get('Accept-Language', 'en')
        
        # Handle JSON requests
        try:
            if request.is_json and request.get_json():
                json_data = request.get_json()
                if isinstance(json_data, dict):
                    lang = json_data.get('lang', lang)
        except:
            pass
        
        # Extract language code (handle cases like 'ar-SA', 'en-US')
        if isinstance(lang, str):
            lang = lang.split('-')[0].split(',')[0].lower()
        
        return 'ar' if lang == 'ar' else 'en'
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password or not isinstance(password, str):
            return False
        return len(password.strip()) >= 6
    
    @staticmethod
    def validate_required_fields(data, required_fields, lang='en'):
        """Validate required fields in request data"""
        from app.localization import LocalizationHelper
        
        errors = []
        
        for field in required_fields:
            if field not in data or not data[field] or str(data[field]).strip() == '':
                field_name = field.replace('_', ' ').title()
                error_msg = LocalizationHelper.get_message(
                    'required_field', lang, field=field_name
                )
                errors.append({
                    'field': field,
                    'message': error_msg
                })
        
        return errors
    
    @staticmethod
    def validate_numeric_field(value, field_name, lang='en'):
        """Validate numeric field"""
        from app.localization import LocalizationHelper
        
        try:
            float(value)
            return None
        except (ValueError, TypeError):
            return LocalizationHelper.get_message(
                'invalid_number', lang, field=field_name
            )
    
    @staticmethod
    def sanitize_string(value, max_length=None):
        """Sanitize string input"""
        if not isinstance(value, str):
            return str(value) if value is not None else ''
        
        # Strip whitespace and limit length
        sanitized = value.strip()
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized