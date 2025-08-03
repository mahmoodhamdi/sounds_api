class LocalizationHelper:
    """Helper class for handling localization in the Flask application"""
    
    MESSAGES = {
        'en': {
            # Authentication messages
            'user_already_exists': 'User already exists',
            'user_not_found': 'User not found',
            'invalid_credentials': 'Invalid email or password',
            'authentication_required': 'Authentication required',
            'admin_access_required': 'Admin access required',
            'access_denied': 'Access denied',
            'invalid_token': 'Invalid or expired token',
            
            # Validation messages
            'required_field': '{field} is required',
            'invalid_email': 'Please provide a valid email address',
            'password_too_short': 'Password must be at least 6 characters long',
            'invalid_number': 'Please provide a valid number for {field}',
            'invalid_format': 'Invalid format for {field}',
            'file_required': 'File is required',
            'no_file_selected': 'No file selected',
            'invalid_file_type': 'Invalid file type. Only images are allowed',
            'file_too_large': 'File size is too large. Maximum size is {size}MB',
            
            # Level management
            'level_not_found': 'Level not found',
            'level_already_assigned': 'Level is already assigned to this user',
            'level_not_purchased': 'Level has not been purchased',
            'level_already_purchased': 'Level has already been purchased',
            'level_created_successfully': 'Level created successfully',
            'level_updated_successfully': 'Level updated successfully',
            'level_deleted_successfully': 'Level deleted successfully',
            
            # Video management
            'video_not_found': 'Video not found',
            'video_not_accessible': 'Video is not accessible',
            'video_must_be_opened': 'Video must be opened before accessing questions',
            'video_completed_successfully': 'Video completed successfully',
            'video_created_successfully': 'Video created successfully',
            'video_updated_successfully': 'Video updated successfully',
            'video_deleted_successfully': 'Video deleted successfully',
            
            # Question management
            'question_not_found': 'Question not found',
            'question_created_successfully': 'Question created successfully',
            'question_updated_successfully': 'Question updated successfully',
            'question_deleted_successfully': 'Question deleted successfully',
            'answer_not_found': 'Answer not found',
            'answer_submitted_successfully': 'Answer submitted successfully',
            
            # Exam management
            'exam_not_available': 'Final exam is not available yet. Please complete all videos first',
            'initial_exam_submitted': 'Initial exam submitted successfully',
            'final_exam_submitted': 'Final exam submitted successfully',
            'exam_already_taken': 'Exam has already been taken',
            
            # User management
            'user_created_successfully': 'User created successfully',
            'user_updated_successfully': 'User updated successfully',
            'user_deleted_successfully': 'User deleted successfully',
            'password_reset_successfully': 'Password reset successfully',
            'level_assigned_successfully': 'Level assigned successfully',
            'level_purchased_successfully': 'Level purchased successfully',
            
            # Welcome video
            'welcome_video_set': 'Welcome video set successfully',
            'welcome_video_not_found': 'No welcome video has been set',
            
            # General messages
            'operation_successful': 'Operation completed successfully',
            'operation_failed': 'Operation failed. Please try again',
            'invalid_request': 'Invalid request data',
            'server_error': 'Internal server error. Please contact support',
            'not_found': 'The requested resource was not found',
            'unauthorized': 'You are not authorized to perform this action',
            'forbidden': 'This action is forbidden',
            'validation_error': 'Please check your input data',
            'database_error': 'Database operation failed. Please try again',
        },
        'ar': {
            # Authentication messages
            'user_already_exists': 'المستخدم موجود بالفعل',
            'user_not_found': 'المستخدم غير موجود',
            'invalid_credentials': 'البريد الإلكتروني أو كلمة المرور غير صحيحة',
            'authentication_required': 'مطلوب تسجيل الدخول',
            'admin_access_required': 'مطلوب صلاحية المدير',
            'access_denied': 'تم رفض الوصول',
            'invalid_token': 'رمز التحقق غير صالح أو منتهي الصلاحية',
            
            # Validation messages
            'required_field': '{field} مطلوب',
            'invalid_email': 'يرجى إدخال عنوان بريد إلكتروني صحيح',
            'password_too_short': 'كلمة المرور يجب أن تكون 6 أحرف على الأقل',
            'invalid_number': 'يرجى إدخال رقم صحيح لـ {field}',
            'invalid_format': 'تنسيق غير صحيح لـ {field}',
            'file_required': 'الملف مطلوب',
            'no_file_selected': 'لم يتم اختيار ملف',
            'invalid_file_type': 'نوع الملف غير صحيح. الصور فقط مسموحة',
            'file_too_large': 'حجم الملف كبير جداً. الحد الأقصى {size} ميجابايت',
            
            # Level management
            'level_not_found': 'المستوى غير موجود',
            'level_already_assigned': 'المستوى مُعين بالفعل لهذا المستخدم',
            'level_not_purchased': 'لم يتم شراء المستوى',
            'level_already_purchased': 'تم شراء المستوى بالفعل',
            'level_created_successfully': 'تم إنشاء المستوى بنجاح',
            'level_updated_successfully': 'تم تحديث المستوى بنجاح',
            'level_deleted_successfully': 'تم حذف المستوى بنجاح',
            
            # Video management
            'video_not_found': 'الفيديو غير موجود',
            'video_not_accessible': 'الفيديو غير متاح',
            'video_must_be_opened': 'يجب فتح الفيديو قبل الوصول للأسئلة',
            'video_completed_successfully': 'تم إكمال الفيديو بنجاح',
            'video_created_successfully': 'تم إنشاء الفيديو بنجاح',
            'video_updated_successfully': 'تم تحديث الفيديو بنجاح',
            'video_deleted_successfully': 'تم حذف الفيديو بنجاح',
            
            # Question management
            'question_not_found': 'السؤال غير موجود',
            'question_created_successfully': 'تم إنشاء السؤال بنجاح',
            'question_updated_successfully': 'تم تحديث السؤال بنجاح',
            'question_deleted_successfully': 'تم حذف السؤال بنجاح',
            'answer_not_found': 'الإجابة غير موجودة',
            'answer_submitted_successfully': 'تم إرسال الإجابة بنجاح',
            
            # Exam management
            'exam_not_available': 'الامتحان النهائي غير متاح بعد. يرجى إكمال جميع الفيديوهات أولاً',
            'initial_exam_submitted': 'تم إرسال الامتحان الأولي بنجاح',
            'final_exam_submitted': 'تم إرسال الامتحان النهائي بنجاح',
            'exam_already_taken': 'تم أداء الامتحان بالفعل',
            
            # User management
            'user_created_successfully': 'تم إنشاء المستخدم بنجاح',
            'user_updated_successfully': 'تم تحديث المستخدم بنجاح',
            'user_deleted_successfully': 'تم حذف المستخدم بنجاح',
            'password_reset_successfully': 'تم إعادة تعيين كلمة المرور بنجاح',
            'level_assigned_successfully': 'تم تعيين المستوى بنجاح',
            'level_purchased_successfully': 'تم شراء المستوى بنجاح',
            
            # Welcome video
            'welcome_video_set': 'تم تعيين فيديو الترحيب بنجاح',
            'welcome_video_not_found': 'لم يتم تعيين فيديو ترحيب',
            
            # General messages
            'operation_successful': 'تمت العملية بنجاح',
            'operation_failed': 'فشلت العملية. يرجى المحاولة مرة أخرى',
            'invalid_request': 'بيانات الطلب غير صحيحة',
            'server_error': 'خطأ في الخادم الداخلي. يرجى الاتصال بالدعم الفني',
            'not_found': 'المورد المطلوب غير موجود',
            'unauthorized': 'غير مخول لتنفيذ هذا الإجراء',
            'forbidden': 'هذا الإجراء محظور',
            'validation_error': 'يرجى التحقق من البيانات المدخلة',
            'database_error': 'فشل في عملية قاعدة البيانات. يرجى المحاولة مرة أخرى',
        }
    }
    
    @classmethod
    def get_message(cls, key, lang='en', **kwargs):
        """Get localized message by key and language"""
        lang = lang.lower() if lang else 'en'
        if lang not in cls.MESSAGES:
            lang = 'en'
        
        message = cls.MESSAGES[lang].get(key, cls.MESSAGES['en'].get(key, key))
        
        # Format message with provided arguments
        if kwargs:
            try:
                message = message.format(**kwargs)
            except (KeyError, ValueError):
                pass
        
        return message
    
    @classmethod
    def get_error_response(cls, key, lang='en', status_code=400, **kwargs):
        """Get formatted error response with localized message"""
        message = cls.get_message(key, lang, **kwargs)
        return {
            'success': False,
            'message': message,
            'message_key': key,
            'lang': lang
        }, status_code
    
    @classmethod
    def get_success_response(cls, key, data=None, lang='en', **kwargs):
        """Get formatted success response with localized message"""
        message = cls.get_message(key, lang, **kwargs)
        response = {
            'success': True,
            'message': message,
            'message_key': key,
            'lang': lang
        }
        
        if data is not None:
            if isinstance(data, dict):
                response.update(data)
            else:
                response['data'] = data
        
        return response, 200
