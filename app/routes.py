import json
import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
from flask import Blueprint, request, jsonify, send_from_directory, current_app, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, bcrypt
from app.models import User, Level, Video, UserLevel, UserVideoProgress, ExamResult, WelcomeVideo, Question, UserQuestionAnswer
from app.auth import admin_required, client_required, authenticate_user, create_user_token
from sqlalchemy.exc import IntegrityError

bp = Blueprint('main', _name_)

# Serve uploaded files
@bp.route('/Uploads/levels/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

# Custom decorator to allow both admin and client roles
def admin_or_client_required(f):
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if user.role not in ['admin', 'client']:
            return jsonify({'message': 'Access denied'}), 403
        return f(*args, **kwargs)
    wrapper._name_ = f._name_
    return wrapper

# Welcome Video Management Routes
@bp.route('/welcome_video', methods=['POST'])
@admin_required
def set_welcome_video():
    data = request.get_json()
    video_url = data.get('video_url')

    if not video_url:
        return jsonify({'message': 'Video URL required'}), 400

    WelcomeVideo.query.delete()
    welcome_video = WelcomeVideo(video_url=video_url)
    db.session.add(welcome_video)
    db.session.commit()

    return jsonify({
        'success': True,
        'video_url': video_url
    }), 200

@bp.route('/welcome_video', methods=['GET'])
def get_welcome_video():
    welcome_video = WelcomeVideo.query.first()

    if not welcome_video:
        return jsonify({'message': 'No welcome video set'}), 404

    return jsonify({
        'video_url': welcome_video.video_url
    }), 200

# Authentication Routes
@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = bcrypt.generate_password_hash(
        data['password']).decode('utf-8')

    user = User(
        name=data['name'],
        email=data['email'],
        password=hashed_password,
        role=data.get('role', 'client'),
        picture=data.get('picture', '')
    )

    db.session.add(user)
    db.session.commit()

    token = create_user_token(user)

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'picture': user.picture,
        'token': token
    }), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    is_google_login = data.get('google', False)

    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if not is_google_login:
        # في تسجيل دخول عادي، نتحقق من الباسورد
        if not bcrypt.check_password_hash(user.password, data['password']):
            return jsonify({'message': 'Invalid credentials'}), 401
    else:
        # لو تسجيل دخول من Google وتأكدنا من الإيميل فقط
        print("Google login: skipping password check")
    token = create_user_token(user)

    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'picture': user.picture,
        'token': token
    }), 200

# User Management Routes
@bp.route('/users/<int:user_id>', methods=['GET'])
@client_required
def get_user(user_id):
    current_user_id = int(get_jwt_identity())

    user = User.query.get(current_user_id)
    if user.role != 'admin' and current_user_id != user_id:
        return jsonify({'message': 'Access denied'}), 403

    target_user = User.query.get_or_404(user_id)

    return jsonify({
        'id': target_user.id,
        'name': target_user.name,
        'email': target_user.email,
        'role': target_user.role,
        'picture': target_user.picture
    }), 200

@bp.route('/users/<int:user_id>', methods=['PUT'])
@client_required
def update_user(user_id):
    current_user_id = int(get_jwt_identity())

    user = User.query.get(current_user_id)
    if user.role != 'admin' and current_user_id != user_id:
        return jsonify({'message': 'Access denied'}), 403

    target_user = User.query.get_or_404(user_id)
    data = request.get_json()

    target_user.name = data.get('name', target_user.name)
    target_user.picture = data.get('picture', target_user.picture)

    if user.role == 'admin':
        target_user.role = data.get('role', target_user.role)

    db.session.commit()

    return jsonify({
        'id': target_user.id,
        'name': target_user.name,
        'email': target_user.email,
        'role': target_user.role,
        'picture': target_user.picture
    }), 200

@bp.route('/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    users = User.query.all()
    result = [{
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'picture': user.picture,
        'level_count': len(user.levels)
    } for user in users]
    return jsonify(result), 200

@bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    UserLevel.query.filter_by(user_id=user_id).delete()
    ExamResult.query.filter_by(user_id=user_id).delete()
    UserQuestionAnswer.query.filter_by(user_id=user_id).delete()

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'}), 200

@bp.route('/admin/users/<int:user_id>/reset_password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    new_password = data.get('new_password')
    if not new_password:
        return jsonify({'message': 'New password required'}), 400

    user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return jsonify({'message': 'Password reset successfully'}), 200

@bp.route('/admin/users/<int:user_id>/assign_level/<int:level_id>', methods=['POST'])
@admin_required
def assign_level_to_user(user_id, level_id):
    user = User.query.get_or_404(user_id)
    level = Level.query.get_or_404(level_id)

    existing_user_level = UserLevel.query.filter_by(user_id=user_id, level_id=level_id).first()
    if existing_user_level:
        return jsonify({'message': 'Level already assigned'}), 400

    user_level = UserLevel(
        user_id=user_id,
        level_id=level_id,
        is_completed=False,
        can_take_final_exam=False
    )

    db.session.add(user_level)
    db.session.flush()

    level_videos = Video.query.filter_by(level_id=level_id).order_by(Video.id).all()

    for i, video in enumerate(level_videos):
        # Check if progress already exists
        existing_progress = UserVideoProgress.query.filter_by(
            user_level_id=user_level.id, video_id=video.id
        ).first()
        if not existing_progress:
            video_progress = UserVideoProgress(
                user_level_id=user_level.id,
                video_id=video.id,
                is_opened=(i == 0),
                is_completed=False
            )
            db.session.add(video_progress)

    db.session.commit()

    return jsonify({'message': 'Level assigned successfully'}), 201

# Level Management Routes
@bp.route('/levels', methods=['POST'])
@admin_required
def create_level():
    data = request.form

    if 'file' not in request.files:
        return jsonify({'message': 'Image file required'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    level_number = data.get('level_number')
    if not level_number or not level_number.isdigit():
        return jsonify({'message': 'Valid level number required'}), 400

    level = Level(
        name=data['name'],
        description=data.get('description', ''),
        level_number=int(level_number),
        welcome_video_url=data.get('welcome_video_url', ''),
        price=float(data['price']),
        initial_exam_question=data.get('initial_exam_question', ''),
        final_exam_question=data.get('final_exam_question', '')
    )

    if file:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'], unique_filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        level.image_path = f"/Uploads/levels/{unique_filename}"

    db.session.add(level)
    db.session.commit()

    return jsonify({
        'id': level.id,
        'name': level.name,
        'description': level.description,
        'level_number': level.level_number,
        'welcome_video_url': level.welcome_video_url,
        'image_path': level.image_path,
        'price': level.price,
        'initial_exam_question': level.initial_exam_question,
        'final_exam_question': level.final_exam_question,
        'videos_count': 0,
        'videos': []
    }), 201

@bp.route('/levels/<int:level_id>', methods=['PUT'])
@admin_required
def update_level(level_id):
    level = Level.query.get_or_404(level_id)
    data = request.form

    level.name = data.get('name', level.name)
    level.description = data.get('description', level.description)
    level.level_number = int(data.get('level_number', level.level_number))
    level.welcome_video_url = data.get(
        'welcome_video_url', level.welcome_video_url)
    level.price = float(data.get('price', level.price))
    level.initial_exam_question = data.get(
        'initial_exam_question', level.initial_exam_question)
    level.final_exam_question = data.get(
        'final_exam_question', level.final_exam_question)

    if 'file' in request.files and request.files['file'].filename:
        file = request.files['file']
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'], unique_filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        level.image_path = f"/Uploads/levels/{unique_filename}"

    db.session.commit()

    return jsonify({
        'id': level.id,
        'name': level.name,
        'description': level.description,
        'level_number': level.level_number,
        'welcome_video_url': level.welcome_video_url,
        'image_path': level.image_path,
        'price': level.price,
        'initial_exam_question': level.initial_exam_question,
        'final_exam_question': level.final_exam_question,
        'videos_count': len(level.videos),
        'videos': [self._format_video_data(v) for v in level.videos]
    }), 200

def _format_video_data(video):
    """Helper function to format video data with questions"""
    questions = Question.query.filter_by(video_id=video.id).order_by(Question.order).all()
    return {
        'id': video.id,
        'youtube_link': video.youtube_link,
        'questions': [{
            'id': q.id,
            'text': q.text,
            'order': q.order
        } for q in questions]
    }

@bp.route('/levels/<int:level_id>', methods=['DELETE'])
@admin_required
def delete_level(level_id):
    level = Level.query.get_or_404(level_id)

    for video in level.videos:
        db.session.delete(video)

    for user_level in level.user_levels:
        db.session.delete(user_level)

    db.session.delete(level)
    db.session.commit()

    return jsonify({'message': 'Level deleted successfully'}), 200

@bp.route('/levels', methods=['GET'])
@admin_or_client_required
def get_levels():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)

    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    level_number = request.args.get('level_number', type=int)
    name = request.args.get('name')

    query = Level.query

    if min_price is not None:
        query = query.filter(Level.price >= min_price)
    if max_price is not None:
        query = query.filter(Level.price <= max_price)
    if level_number is not None:
        query = query.filter(Level.level_number == level_number)
    if name:
        query = query.filter(Level.name.ilike(f'%{name}%'))

    levels = query.order_by(Level.level_number).all()
    result = []

    for level in levels:
        level_data = {
            'id': level.id,
            'name': level.name,
            'description': level.description,
            'level_number': level.level_number,
            'welcome_video_url': level.welcome_video_url,
            'image_path': level.image_path,
            'price': level.price,
            'initial_exam_question': level.initial_exam_question,
            'final_exam_question': level.final_exam_question,
            'videos_count': len(level.videos),
            'videos': [],
            'is_completed': False,
            'can_take_final_exam': False
        }

        user_level = UserLevel.query.filter_by(
            user_id=current_user_id, level_id=level.id).first()
        if user_level:
            level_data['is_completed'] = user_level.is_completed
            level_data['can_take_final_exam'] = user_level.can_take_final_exam

            for video in level.videos:
                video_progress = UserVideoProgress.query.filter_by(
                    user_level_id=user_level.id,
                    video_id=video.id
                ).first()

                # Get questions for this video
                questions = Question.query.filter_by(video_id=video.id).order_by(Question.order).all()
                questions_data = []
                
                if user.role == 'admin' or (video_progress and video_progress.is_opened):
                    for question in questions:
                        question_data = {
                            'id': question.id,
                            'text': question.text,
                            'order': question.order
                        }
                        
                        # Add user's answer if exists
                        if user.role == 'client':
                            user_answer = UserQuestionAnswer.query.filter_by(
                                user_id=current_user_id, question_id=question.id
                            ).first()
                            if user_answer:
                                question_data['user_answer'] = {
                                    'correct_words': user_answer.correct_words,
                                    'wrong_words': user_answer.wrong_words,
                                    'percentage': user_answer.percentage,
                                    'submitted_at': user_answer.submitted_at.isoformat()
                                }
                        
                        questions_data.append(question_data)

                video_data = {
                    'id': video.id,
                    'youtube_link': video.youtube_link if user.role == 'admin' else (video.youtube_link if video_progress and video_progress.is_opened else ''),
                    'questions': questions_data,
                    'is_opened': video_progress.is_opened if video_progress else False
                }
                level_data['videos'].append(video_data)
        else:
            level_data['videos'] = [{'id': v.id, 'youtube_link': '', 'questions': []} for v in level.videos]

        if user.role == 'admin':
            level_data['user_count'] = len(level.user_levels)

        result.append(level_data)

    return jsonify(result), 200

@bp.route('/admin/levels', methods=['GET'])
@admin_required
def admin_get_all_levels():
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    level_number = request.args.get('level_number', type=int)
    name = request.args.get('name')

    query = Level.query

    if min_price is not None:
        query = query.filter(Level.price >= min_price)
    if max_price is not None:
        query = query.filter(Level.price <= max_price)
    if level_number is not None:
        query = query.filter(Level.level_number == level_number)
    if name:
        query = query.filter(Level.name.ilike(f'%{name}%'))

    levels = query.order_by(Level.level_number).all()
    result = [{
        'id': level.id,
        'name': level.name,
        'description': level.description,
        'level_number': level.level_number,
        'welcome_video_url': level.welcome_video_url,
        'image_path': level.image_path,
        'price': level.price,
        'initial_exam_question': level.initial_exam_question,
        'final_exam_question': level.final_exam_question,
        'videos_count': len(level.videos),
        'videos': [_format_video_data(v) for v in level.videos],
        'user_count': len(level.user_levels)
    } for level in levels]
    return jsonify(result), 200

@bp.route('/levels/<int:level_id>', methods=['GET'])
@client_required
def get_level(level_id):
    current_user_id = int(get_jwt_identity())
    level = Level.query.get_or_404(level_id)

    level_data = {
        'id': level.id,
        'name': level.name,
        'description': level.description,
        'level_number': level.level_number,
        'welcome_video_url': level.welcome_video_url,
        'image_path': level.image_path,
        'price': level.price,
        'initial_exam_question': level.initial_exam_question,
        'final_exam_question': level.final_exam_question,
        'videos_count': len(level.videos),
        'videos': [],
        'is_completed': False,
        'can_take_final_exam': False
    }

    user_level = UserLevel.query.filter_by(
        user_id=current_user_id, level_id=level.id).first()
    if user_level:
        level_data['is_completed'] = user_level.is_completed
        level_data['can_take_final_exam'] = user_level.can_take_final_exam

        for video in level.videos:
            video_progress = UserVideoProgress.query.filter_by(
                user_level_id=user_level.id,
                video_id=video.id
            ).first()

            # Get questions for this video
            questions = Question.query.filter_by(video_id=video.id).order_by(Question.order).all()
            questions_data = []
            
            for question in questions:
                question_data = {
                    'id': question.id,
                    'text': question.text,
                    'order': question.order
                }
                
                # Add user's answer if exists
                user_answer = UserQuestionAnswer.query.filter_by(
                    user_id=current_user_id, question_id=question.id
                ).first()
                if user_answer:
                    question_data['user_answer'] = {
                        'correct_words': user_answer.correct_words,
                        'wrong_words': user_answer.wrong_words,
                        'percentage': user_answer.percentage,
                        'submitted_at': user_answer.submitted_at.isoformat()
                    }
                
                questions_data.append(question_data)

            video_data = {
                'id': video.id,
                'youtube_link': video.youtube_link,
                'questions': questions_data,
                'is_opened': video_progress.is_opened if video_progress else False
            }
            level_data['videos'].append(video_data)
    else:
        level_data['videos'] = [{'id': v.id, 'youtube_link': '', 'questions': []} for v in level.videos]

    return jsonify(level_data), 200

# Video Management Routes
@bp.route('/levels/<int:level_id>/videos', methods=['POST'])
@admin_required
def add_video_to_level(level_id):
    level = Level.query.get_or_404(level_id)
    data = request.get_json()

    video = Video(
        level_id=level_id,
        youtube_link=data['youtube_link']
    )

    db.session.add(video)
    db.session.commit()

    return jsonify({
        'id': video.id,
        'youtube_link': video.youtube_link,
        'questions': []
    }), 201

@bp.route('/videos/<int:video_id>', methods=['PUT'])
@admin_required
def update_video(video_id):
    video = Video.query.get_or_404(video_id)
    data = request.get_json()

    video.youtube_link = data.get('youtube_link', video.youtube_link)
    db.session.commit()

    return jsonify({
        'id': video.id,
        'youtube_link': video.youtube_link,
        'questions': [{'id': q.id, 'text': q.text, 'order': q.order} for q in video.questions]
    }), 200

@bp.route('/videos/<int:video_id>', methods=['DELETE'])
@admin_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)

    user_progresses = UserVideoProgress.query.filter_by(video_id=video_id).all()
    for progress in user_progresses:
        db.session.delete(progress)

    db.session.delete(video)
    db.session.commit()

    return jsonify({'message': 'Video deleted successfully'}), 200

@bp.route('/admin/videos', methods=['GET'])
@admin_required
def get_all_videos():
    videos = Video.query.all()
    result = [{
        'id': video.id,
        'level_id': video.level_id,
        'level_name': video.level.name if video.level else '',
        'youtube_link': video.youtube_link,
        'questions': [{'id': q.id, 'text': q.text, 'order': q.order} for q in video.questions],
        'user_progress_count': UserVideoProgress.query.filter_by(video_id=video.id).count()
    } for video in videos]
    return jsonify(result), 200

# Question Management Routes (CRUD)
@bp.route('/videos/<int:video_id>/questions', methods=['POST'])
@admin_required
def create_question(video_id):
    video = Video.query.get_or_404(video_id)
    data = request.get_json()

    # Get the next order number
    max_order = db.session.query(db.func.max(Question.order)).filter_by(video_id=video_id).scalar() or 0
    
    question = Question(
        video_id=video_id,
        text=data['text'],
        order=data.get('order', max_order + 1)
    )

    db.session.add(question)
    db.session.commit()

    return jsonify({
        'id': question.id,
        'video_id': question.video_id,
        'text': question.text,
        'order': question.order,
        'created_at': question.created_at.isoformat()
    }), 201

@bp.route('/questions/<int:question_id>', methods=['PUT'])
@admin_required
def update_question(question_id):
    question = Question.query.get_or_404(question_id)
    data = request.get_json()

    question.text = data.get('text', question.text)
    question.order = data.get('order', question.order)
    db.session.commit()

    return jsonify({
        'id': question.id,
        'video_id': question.video_id,
        'text': question.text,
        'order': question.order,
        'created_at': question.created_at.isoformat()
    }), 200

@bp.route('/questions/<int:question_id>', methods=['DELETE'])
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    # Delete all user answers for this question
    UserQuestionAnswer.query.filter_by(question_id=question_id).delete()
    
    db.session.delete(question)
    db.session.commit()

    return jsonify({'message': 'Question deleted successfully'}), 200

@bp.route('/admin/questions', methods=['GET'])
@admin_required
def get_all_questions():
    questions = Question.query.order_by(Question.video_id, Question.order).all()
    result = [{
        'id': question.id,
        'video_id': question.video_id,
        'video_link': question.video.youtube_link if question.video else '',
        'level_name': question.video.level.name if question.video and question.video.level else '',
        'text': question.text,
        'order': question.order,
        'created_at': question.created_at.isoformat(),
        'answers_count': UserQuestionAnswer.query.filter_by(question_id=question.id).count()
    } for question in questions]
    return jsonify(result), 200

@bp.route('/videos/<int:video_id>/questions', methods=['GET'])
@admin_or_client_required
def get_video_questions(video_id):
    video = Video.query.get_or_404(video_id)
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    questions = Question.query.filter_by(video_id=video_id).order_by(Question.order).all()
    result = []
    
    for question in questions:
        question_data = {
            'id': question.id,
            'video_id': question.video_id,
            'text': question.text,
            'order': question.order,
            'created_at': question.created_at.isoformat()
        }
        
        # Add user's answer if client and answer exists
        if user.role == 'client':
            user_answer = UserQuestionAnswer.query.filter_by(
                user_id=current_user_id, question_id=question.id
            ).first()
            if user_answer:
                question_data['user_answer'] = {
                    'correct_words': user_answer.correct_words,
                    'wrong_words': user_answer.wrong_words,
                    'percentage': user_answer.percentage,
                    'correct_words_list': json.loads(user_answer.correct_words_list) if user_answer.correct_words_list else [],
                    'wrong_words_list': json.loads(user_answer.wrong_words_list) if user_answer.wrong_words_list else [],
                    'submitted_at': user_answer.submitted_at.isoformat()
                }
        
        result.append(question_data)
    
    return jsonify(result), 200

# Question Answer Submission Routes
@bp.route('/questions/<int:question_id>/submit', methods=['POST'])
@client_required
def submit_question_answer(question_id):
    current_user_id = int(get_jwt_identity())
    question = Question.query.get_or_404(question_id)
    data = request.get_json()

    # Validate required fields
    if 'correct_words' not in data or 'wrong_words' not in data:
        return jsonify({'message': 'correct_words and wrong_words are required'}), 400

    correct_words = data['correct_words']
    wrong_words = data['wrong_words']
    total_words = correct_words + wrong_words
    percentage = (correct_words / total_words * 100) if total_words > 0 else 0

    # Check if user has access to this question (through video access)
    user_level = UserLevel.query.join(Level).join(Video).filter(
        UserLevel.user_id == current_user_id,
        Video.id == question.video_id
    ).first()
    
    if not user_level:
        return jsonify({'message': 'Access denied. You need to purchase the level first.'}), 403

    # Check if video is opened
    video_progress = UserVideoProgress.query.filter_by(
        user_level_id=user_level.id,
        video_id=question.video_id
    ).first()
    
    if not video_progress or not video_progress.is_opened:
        return jsonify({'message': 'Video must be opened first'}), 400

    # Check if answer already exists, update if it does
    existing_answer = UserQuestionAnswer.query.filter_by(
        user_id=current_user_id, question_id=question_id
    ).first()

    if existing_answer:
        existing_answer.correct_words = correct_words
        existing_answer.wrong_words = wrong_words
        existing_answer.percentage = percentage
        existing_answer.correct_words_list = json.dumps(data.get('correct_words_list', []))
        existing_answer.wrong_words_list = json.dumps(data.get('wrong_words_list', []))
        existing_answer.submitted_at = datetime.utcnow()
        answer = existing_answer
    else:
        answer = UserQuestionAnswer(
            user_id=current_user_id,
            question_id=question_id,
            correct_words=correct_words,
            wrong_words=wrong_words,
            percentage=percentage,
            correct_words_list=json.dumps(data.get('correct_words_list', [])),
            wrong_words_list=json.dumps(data.get('wrong_words_list', []))
        )
        db.session.add(answer)

    db.session.commit()

    return jsonify({
        'id': answer.id,
        'question_id': question_id,
        'question_text': question.text,
        'correct_words': answer.correct_words,
        'wrong_words': answer.wrong_words,
        'percentage': answer.percentage,
        'correct_words_list': json.loads(answer.correct_words_list) if answer.correct_words_list else [],
        'wrong_words_list': json.loads(answer.wrong_words_list) if answer.wrong_words_list else [],
        'submitted_at': answer.submitted_at.isoformat()
    }), 200

@bp.route('/users/<int:user_id>/questions/<int:question_id>/answer', methods=['GET'])
@client_required
def get_user_question_answer(user_id, question_id):
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    
    # Check access permissions
    if user.role != 'admin' and current_user_id != user_id:
        return jsonify({'message': 'Access denied'}), 403

    answer = UserQuestionAnswer.query.filter_by(
        user_id=user_id, question_id=question_id
    ).first()
    
    if not answer:
        return jsonify({'message': 'Answer not found'}), 404

    question = Question.query.get(question_id)
    
    return jsonify({
        'id': answer.id,
        'question_id': question_id,
        'question_text': question.text if question else '',
        'correct_words': answer.correct_words,
        'wrong_words': answer.wrong_words,
        'percentage': answer.percentage,
        'correct_words_list': json.loads(answer.correct_words_list) if answer.correct_words_list else [],
        'wrong_words_list': json.loads(answer.wrong_words_list) if answer.wrong_words_list else [],
        'submitted_at': answer.submitted_at.isoformat()
    }), 200

@bp.route('/admin/questions/<int:question_id>/answers', methods=['GET'])
@admin_required
def get_question_answers(question_id):
    question = Question.query.get_or_404(question_id)
    answers = UserQuestionAnswer.query.filter_by(question_id=question_id).all()
    
    result = [{
        'id': answer.id,
        'user_id': answer.user_id,
        'user_name': answer.user.name if answer.user else '',
        'correct_words': answer.correct_words,
        'wrong_words': answer.wrong_words,
        'percentage': answer.percentage,
        'correct_words_list': json.loads(answer.correct_words_list) if answer.correct_words_list else [],
        'wrong_words_list': json.loads(answer.wrong_words_list) if answer.wrong_words_list else [],
        'submitted_at': answer.submitted_at.isoformat()
    } for answer in answers]
    
    return jsonify({
        'question_id': question_id,
        'question_text': question.text,
        'answers': result
    }), 200

@bp.route('/users/<int:user_id>/levels/<int:level_id>/videos/<int:video_id>/complete', methods=['PATCH'])
@client_required
def complete_video(user_id, level_id, video_id):
    current_user_id = int(get_jwt_identity())

    user = User.query.get(current_user_id)
    if user.role != 'admin' and current_user_id != user_id:
        return jsonify({'message': 'Access denied'}), 403

    user_level = UserLevel.query.filter_by(
        user_id=user_id, level_id=level_id).first()
    if not user_level:
        return jsonify({'message': 'Level not purchased'}), 400

    video_progress = UserVideoProgress.query.filter_by(
        user_level_id=user_level.id,
        video_id=video_id
    ).first()

    if not video_progress:
        return jsonify({'message': 'Video not accessible'}), 400

    video_progress.is_completed = True

    level_videos = Video.query.filter_by(
        level_id=level_id).order_by(Video.id).all()

    current_video_index = None
    for i, video in enumerate(level_videos):
        if video.id == video_id:
            current_video_index = i
            break

    if current_video_index is not None and (current_video_index + 1) < len(level_videos):
        next_video = level_videos[current_video_index + 1]
        next_video_progress = UserVideoProgress.query.filter_by(
            user_level_id=user_level.id,
            video_id=next_video.id
        ).first()

        if next_video_progress:
            next_video_progress.is_opened = True

    all_videos_completed = all(
        UserVideoProgress.query.filter_by(
            user_level_id=user_level.id,
            video_id=video.id
        ).first().is_completed
        for video in level_videos
    )

    if all_videos_completed:
        user_level.can_take_final_exam = True

    db.session.commit()

    return jsonify({'message': 'Video completed successfully'}), 200

# Exam Routes
@bp.route('/exams/<int:level_id>/initial', methods=['POST'])
@client_required
def submit_initial_exam(level_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    user_level = UserLevel.query.filter_by(
        user_id=current_user_id, level_id=level_id).first()
    if not user_level:
        return jsonify({'message': 'Level not purchased'}), 400

    total_words = data['correct_words'] + data['wrong_words']
    percentage = (data['correct_words'] / total_words *
                  100) if total_words > 0 else 0

    exam_result = ExamResult(
        user_id=current_user_id,
        level_id=level_id,
        correct_words=data['correct_words'],
        wrong_words=data['wrong_words'],
        percentage=percentage,
        type='initial',
        correct_words_list=json.dumps(data.get('correct_words_list', [])),
        wrong_words_list=json.dumps(data.get('wrong_words_list', []))
    )

    user_level.initial_exam_score = percentage

    db.session.add(exam_result)
    db.session.commit()

    return jsonify({
        'user_id': current_user_id,
        'level_id': level_id,
        'correct_words': data['correct_words'],
        'wrong_words': data['wrong_words'],
        'percentage': percentage,
        'type': 'initial'
    }), 201

@bp.route('/exams/<int:level_id>/final', methods=['POST'])
@client_required
def submit_final_exam(level_id):
    current_user_id = int(get_jwt_identity())
    data = request.get_json()

    user_level = UserLevel.query.filter_by(
        user_id=current_user_id, level_id=level_id).first()
    if not user_level:
        return jsonify({'message': 'Level not purchased'}), 400

    if not user_level.can_take_final_exam:
        return jsonify({'message': 'Final exam not available yet. Complete all videos first.'}), 400

    total_words = data['correct_words'] + data['wrong_words']
    percentage = (data['correct_words'] / total_words *
                  100) if total_words > 0 else 0

    exam_result = ExamResult(
        user_id=current_user_id,
        level_id=level_id,
        correct_words=data['correct_words'],
        wrong_words=data['wrong_words'],
        percentage=percentage,
        type='final',
        correct_words_list=json.dumps(data.get('correct_words_list', [])),
        wrong_words_list=json.dumps(data.get('wrong_words_list', []))
    )

    user_level.final_exam_score = percentage
    if user_level.initial_exam_score is not None:
        user_level.score_difference = percentage - user_level.initial_exam_score

    user_level.is_completed = True

    db.session.add(exam_result)
    db.session.commit()

    return jsonify({
        'user_id': current_user_id,
        'level_id': level_id,
        'correct_words': data['correct_words'],
        'wrong_words': data['wrong_words'],
        'percentage': percentage,
        'type': 'final'
    }), 201

@bp.route('/exams/<int:level_id>/user/<int:user_id>', methods=['GET'])
@client_required
def get_user_exam_results(level_id, user_id):
    current_user_id = int(get_jwt_identity())

    user = User.query.get(current_user_id)
    if user.role != 'admin' and current_user_id != user_id:
        return jsonify({'message': 'Access denied'}), 403

    exam_results = ExamResult.query.filter_by(
        user_id=user_id, level_id=level_id).all()

    results = [{
        'user_id': exam.user_id,
        'level_id': exam.level_id,
        'correct_words': exam.correct_words,
        'wrong_words': exam.wrong_words,
        'percentage': exam.percentage,
        'type': exam.type,
        'timestamp': exam.timestamp.isoformat()
    } for exam in exam_results]

    return jsonify(results), 200

@bp.route('/admin/exams', methods=['GET'])
@admin_required
def get_all_exam_results():
    exam_results = ExamResult.query.all()
    result = [{
        'id': exam.id,
        'user_id': exam.user_id,
        'user_name': exam.user.name if exam.user else '',
        'level_id': exam.level_id,
        'level_name': exam.level.name if exam.level else '',
        'correct_words': exam.correct_words,
        'wrong_words': exam.wrong_words,
        'percentage': exam.percentage,
        'type': exam.type,
        'timestamp': exam.timestamp.isoformat()
    } for exam in exam_results]
    return jsonify(result), 200

# Report Route
@bp.route('/report', methods=['GET'])
@client_required
def get_user_report():
    current_user_id = int(get_jwt_identity())
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    output_format = request.args.get('format', 'markdown').lower()

    # Gather user data
    user_data = {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'picture': user.picture or 'Not set'
    }

    user_levels = UserLevel.query.filter_by(user_id=current_user_id).all()
    levels_data = []

    for user_level in user_levels:
        level = user_level.level
        videos_progress = UserVideoProgress.query.filter_by(
            user_level_id=user_level.id).all()
        videos_data = []

        for progress in videos_progress:
            video = Video.query.get(progress.video_id)
            
            # Get questions and answers for this video
            questions = Question.query.filter_by(video_id=video.id).order_by(Question.order).all()
            questions_data = []
            
            for question in questions:
                user_answer = UserQuestionAnswer.query.filter_by(
                    user_id=current_user_id, question_id=question.id
                ).first()
                
                question_data = {
                    'question_id': question.id,
                    'question_text': question.text,
                    'question_order': question.order
                }
                
                if user_answer:
                    question_data.update({
                        'correct_words': user_answer.correct_words,
                        'wrong_words': user_answer.wrong_words,
                        'percentage': user_answer.percentage,
                        'correct_words_list': json.loads(user_answer.correct_words_list) if user_answer.correct_words_list else [],
                        'wrong_words_list': json.loads(user_answer.wrong_words_list) if user_answer.wrong_words_list else [],
                        'submitted_at': user_answer.submitted_at.isoformat()
                    })
                else:
                    question_data.update({
                        'correct_words': None,
                        'wrong_words': None,
                        'percentage': None,
                        'correct_words_list': [],
                        'wrong_words_list': [],
                        'submitted_at': None
                    })
                
                questions_data.append(question_data)
            
            videos_data.append({
                'video_id': video.id,
                'youtube_link': video.youtube_link,
                'is_opened': progress.is_opened,
                'is_completed': progress.is_completed,
                'questions': questions_data
            })

        exams = ExamResult.query.filter_by(
            user_id=current_user_id, level_id=level.id).all()
        exams_data = []

        for exam in exams:
            exams_data.append({
                'type': exam.type,
                'correct_words': exam.correct_words,
                'wrong_words': exam.wrong_words,
                'percentage': exam.percentage,
                'correct_words_list': json.loads(exam.correct_words_list) if exam.correct_words_list else [],
                'wrong_words_list': json.loads(exam.wrong_words_list) if exam.wrong_words_list else [],
                'timestamp': exam.timestamp.isoformat()
            })

        level_data = {
            'level_id': level.id,
            'level_name': level.name,
            'level_description': level.description or 'No description',
            'level_number': level.level_number,
            'is_completed': user_level.is_completed,
            'can_take_final_exam': user_level.can_take_final_exam,
            'initial_exam_score': user_level.initial_exam_score,
            'final_exam_score': user_level.final_exam_score,
            'score_difference': user_level.score_difference,
            'videos': videos_data,
            'exams': exams_data
        }

        levels_data.append(level_data)

    if output_format == 'json':
        # Return JSON response
        report = {
            'user': user_data,
            'levels': levels_data
        }
        return jsonify(report), 200
    else:
        # Generate Markdown content
        markdown_content = f"""
# User Progress Report

Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

## User Information

- *Name*: {user_data['name']}
- *Email*: {user_data['email']}
- *User ID*: {user_data['id']}
- *Role*: {user_data['role'].capitalize()}
- *Picture*: {user_data['picture']}

## Levels Progress

{'*No levels enrolled.*' if not levels_data else ''}

"""
        for level in levels_data:
            markdown_content += f"""
### Level: {level['level_name']} (ID: {level['level_id']})

- *Description*: {level['level_description']}
- *Level Number*: {level['level_number']}
- *Status*: {'Completed' if level['is_completed'] else 'In Progress'}
- *Can Take Final Exam*: {'Yes' if level['can_take_final_exam'] else 'No'}
- *Initial Exam Score*: {round(level['initial_exam_score'], 2) if level['initial_exam_score'] is not None else 'Not taken'}
- *Final Exam Score*: {round(level['final_exam_score'], 2) if level['final_exam_score'] is not None else 'Not taken'}
- *Score Difference*: {round(level['score_difference'], 2) if level['score_difference'] is not None else 'N/A'}

#### Videos and Questions

"""
            for video in level['videos']:
                markdown_content += f"""
##### Video ID: {video['video_id']}
- *YouTube Link*: {video['youtube_link']}
- *Opened*: {'Yes' if video['is_opened'] else 'No'}
- *Completed*: {'Yes' if video['is_completed'] else 'No'}

*Questions:*

| Question ID | Text | Order | Correct Words | Wrong Words | Percentage | Correct Words List | Wrong Words List | Submitted At |
|-------------|------|-------|---------------|-------------|------------|--------------------|------------------|--------------|
"""
                for question in video['questions']:
                    markdown_content += f"""
| {question['question_id']} | {question['question_text'][:50]}... | {question['question_order']} | {question['correct_words'] if question['correct_words'] is not None else 'N/A'} | {question['wrong_words'] if question['wrong_words'] is not None else 'N/A'} | {round(question['percentage'], 2) if question['percentage'] is not None else 'N/A'} | {', '.join(question['correct_words_list']) if question['correct_words_list'] else 'None'} | {', '.join(question['wrong_words_list']) if question['wrong_words_list'] else 'None'} | {question['submitted_at'] if question['submitted_at'] else 'Not submitted'} |
"""

            markdown_content += f"""
#### Exams

| Type | Timestamp | Correct Words | Wrong Words | Percentage | Correct Words List | Wrong Words List |
|------|-----------|---------------|-------------|------------|--------------------|------------------|
"""
            for exam in level['exams']:
                markdown_content += f"""
| {exam['type'].capitalize()} | {exam['timestamp']} | {exam['correct_words']} | {exam['wrong_words']} | {round(exam['percentage'], 2)} | {', '.join(exam['correct_words_list']) if exam['correct_words_list'] else 'None'} | {', '.join(exam['wrong_words_list']) if exam['wrong_words_list'] else 'None'} |
"""
        
        # Prepare Markdown response
        response = make_response(markdown_content)
        response.headers['Content-Type'] = 'text/markdown'
        response.headers['Content-Disposition'] = f'inline; filename=user_report_{user.id}.md'
        return response

# User Progress Routes
@bp.route('/users/<int:user_id>/levels', methods=['GET'])
@client_required
def get_user_levels(user_id):
    current_user_id = int(get_jwt_identity())

    user = User.query.get(current_user_id)
    if user.role != 'admin' and current_user_id != user_id:
        return jsonify({'message': 'Access denied'}), 403

    user_levels = UserLevel.query.filter_by(user_id=user_id).all()

    result = []
    for user_level in user_levels:
        level = user_level.level

        videos_progress = []
        completed_videos_count = 0

        for video in level.videos:
            video_progress = UserVideoProgress.query.filter_by(
                user_level_id=user_level.id,
                video_id=video.id
            ).first()

            if video_progress:
                videos_progress.append({
                    'video_id': video.id,
                    'is_opened': video_progress.is_opened,
                    'is_completed': video_progress.is_completed
                })
                if video_progress.is_completed:
                    completed_videos_count += 1
            else:
                videos_progress.append({
                    'video_id': video.id,
                    'is_opened': False,
                    'is_completed': False
                })

        level_data = {
            'user_id': user_id,
            'level_id': level.id,
            'level_name': level.name,
            'level_number': level.level_number,
            'completed_videos_count': completed_videos_count,
            'total_videos_count': len(level.videos),
            'videos_progress': videos_progress,
            'is_completed': user_level.is_completed,
            'can_take_final_exam': user_level.can_take_final_exam,
            'initial_exam_score': user_level.initial_exam_score,
            'final_exam_score': user_level.final_exam_score,
            'score_difference': user_level.score_difference
        }

        result.append(level_data)

    return jsonify(result), 200

@bp.route('/users/<int:user_id>/levels/<int:level_id>/purchase', methods=['POST'])
@client_required
def purchase_level(user_id, level_id):
    current_user_id = int(get_jwt_identity())

    user = User.query.get(current_user_id)
    if user.role != 'admin' and current_user_id != user_id:
        return jsonify({'message': 'Access denied'}), 403

    level = Level.query.get_or_404(level_id)

    existing_user_level = UserLevel.query.filter_by(
        user_id=user_id, level_id=level_id).first()
    if existing_user_level:
        return jsonify({'message': 'Level already purchased'}), 400

    user_level = UserLevel(
        user_id=user_id,
        level_id=level_id,
        is_completed=False,
        can_take_final_exam=False
    )

    db.session.add(user_level)
    db.session.flush()

    level_videos = Video.query.filter_by(
        level_id=level_id).order_by(Video.id).all()

    try:
        for i, video in enumerate(level_videos):
            # Check if progress already exists
            existing_progress = UserVideoProgress.query.filter_by(
                user_level_id=user_level.id, video_id=video.id
            ).first()
            if not existing_progress:
                video_progress = UserVideoProgress(
                    user_level_id=user_level.id,
                    video_id=video.id,
                    is_opened=(i == 0),
                    is_completed=False
                )
                db.session.add(video_progress)

        db.session.commit()
        return jsonify({'message': 'Level purchased successfully'}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Failed to purchase level due to existing video progress'}), 400

@bp.route('/users/<int:user_id>/levels/<int:level_id>/update_progress', methods=['PATCH'])
@client_required
def update_level_progress(user_id, level_id):
    current_user_id = int(get_jwt_identity())

    user = User.query.get(current_user_id)
    if user.role != 'admin' and current_user_id != user_id:
        return jsonify({'message': 'Access denied'}), 403

    user_level = UserLevel.query.filter_by(
        user_id=user_id, level_id=level_id).first()
    if not user_level:
        return jsonify({'message': 'Level not purchased'}), 400

    completed_videos = UserVideoProgress.query.filter_by(
        user_level_id=user_level.id,
        is_completed=True
    ).count()

    total_videos = Video.query.filter_by(level_id=level_id).count()

    if completed_videos == total_videos:
        user_level.can_take_final_exam = True

    db.session.commit()

    return jsonify({
        'completed_videos_count': completed_videos,
        'total_videos_count': total_videos,
        'can_take_final_exam': user_level.can_take_final_exam
    }), 200

# Statistics Routes (Admin only)
@bp.route('/admin/statistics', methods=['GET'])
@admin_required
def get_admin_statistics():
    total_users = User.query.filter_by(role='client').count()
    total_levels = Level.query.count()
    total_purchases = UserLevel.query.count()
    completed_levels = UserLevel.query.filter_by(is_completed=True).count()

    completion_rate = (completed_levels / total_purchases *
                       100) if total_purchases > 0 else 0

    popular_levels = db.session.query(
        Level.name,
        db.func.count(UserLevel.id).label('purchases')
    ).join(UserLevel).group_by(Level.id).order_by(db.desc('purchases')).limit(5).all()

    return jsonify({
        'total_users': total_users,
        'total_levels': total_levels,
        'total_purchases': total_purchases,
        'completed_levels': completed_levels,
        'completion_rate': round(completion_rate, 2),
        'popular_levels': [{'name': level, 'purchases': purchases} for level, purchases in popular_levels]
    }), 200

@bp.route('/admin/users/<int:user_id>/statistics', methods=['GET'])
@admin_required
def get_user_statistics(user_id):
    user = User.query.get_or_404(user_id)

    purchased_levels = UserLevel.query.filter_by(user_id=user_id).count()
    completed_levels = UserLevel.query.filter_by(
        user_id=user_id, is_completed=True).count()

    exam_results = ExamResult.query.filter_by(user_id=user_id).all()

    initial_scores = [
        exam.percentage for exam in exam_results if exam.type == 'initial']
    final_scores = [
        exam.percentage for exam in exam_results if exam.type == 'final']

    avg_initial_score = sum(initial_scores) / \
        len(initial_scores) if initial_scores else 0
    avg_final_score = sum(final_scores) / \
        len(final_scores) if final_scores else 0
    avg_improvement = avg_final_score - \
        avg_initial_score if initial_scores and final_scores else 0

    # Question statistics
    total_questions_answered = UserQuestionAnswer.query.filter_by(user_id=user_id).count()
    avg_question_score = db.session.query(db.func.avg(UserQuestionAnswer.percentage)).filter_by(user_id=user_id).scalar() or 0

    return jsonify({
        'user_id': user_id,
        'user_name': user.name,
        'purchased_levels': purchased_levels,
        'completed_levels': completed_levels,
        'completion_rate': round((completed_levels / purchased_levels * 100) if purchased_levels > 0 else 0, 2),
        'average_initial_score': round(avg_initial_score, 2),
        'average_final_score': round(avg_final_score, 2),
        'average_improvement': round(avg_improvement, 2),
        'total_exams_taken': len(exam_results),
        'total_questions_answered': total_questions_answered,
        'average_question_score': round(avg_question_score, 2)
    }), 200