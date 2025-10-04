from datetime import datetime
from app import db

class WelcomeVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_url = db.Column(db.String(200), nullable=False)

    def _repr_(self):
        return f'WelcomeVideo(\'{self.video_url}\')'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(20), nullable=True)  # New phone number column
    role = db.Column(db.String(20), default='client') # 'admin' or 'client'
    picture = db.Column(db.String(200), nullable=True)
    levels = db.relationship('UserLevel', backref='user', lazy=True)

    def _repr_(self):
        return f'User(\'{self.name}\', \'{self.email}\', \'{self.role}\')'

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

    def _repr_(self):
        return f'Level(\'{self.name}\', {self.price})'

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)  # NEW FIELD
    youtube_link = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=1)  # NEW FIELD for ordering
    questions = db.relationship('Question', backref='video', lazy=True, cascade='all, delete-orphan')

    def _repr_(self):
        return f'Video(\'{self.name}\', \'{self.youtube_link}\')'

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with user answers
    user_answers = db.relationship('UserQuestionAnswer', backref='question', lazy=True, cascade='all, delete-orphan')

    def _repr_(self):
        return f'Question(Video: {self.video_id}, Order: {self.order})'

class UserLevel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    can_take_final_exam = db.Column(db.Boolean, default=False)
    initial_exam_score = db.Column(db.Float, nullable=True)
    final_exam_score = db.Column(db.Float, nullable=True)
    score_difference = db.Column(db.Float, nullable=True)
    videos_progress = db.relationship('UserVideoProgress', backref='user_level', lazy=True)

    def _repr_(self):
        return f'UserLevel(User: {self.user_id}, Level: {self.level_id})'

class UserVideoProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_level_id = db.Column(db.Integer, db.ForeignKey('user_level.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    is_opened = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)

    # Add unique constraint on user_level_id and video_id
    _table_args_ = (
        db.UniqueConstraint('user_level_id', 'video_id', name='uq_user_level_video'),
    )

    def _repr_(self):
        return f'UserVideoProgress(UserLevel: {self.user_level_id}, Video: {self.video_id}, Opened: {self.is_opened}, Completed: {self.is_completed})'

class UserQuestionAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    speechace_response = db.Column(db.Text, nullable=True) 
    percentage = db.Column(db.Float, nullable=False, default=0.0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add unique constraint on user_id and question_id
    _table_args_ = (
        db.UniqueConstraint('user_id', 'question_id', name='uq_user_question'),
    )

    # Relationships
    user = db.relationship('User', backref='question_answers')

    def _repr_(self):
        return f'UserQuestionAnswer(User: {self.user_id}, Question: {self.question_id}, Percentage: {self.percentage})'

class ExamResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    speechace_response = db.Column(db.Text, nullable=True)
    percentage = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    

    def _repr_(self):
        return f'ExamResult(User: {self.user_id}, Level: {self.level_id}, Type: {self.type}, Score: {self.percentage})'