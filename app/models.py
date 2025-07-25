from datetime import datetime
from app import db

class WelcomeVideo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    video_url = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'WelcomeVideo(\'{self.video_url}\')'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), default='client') # 'admin' or 'client'
    picture = db.Column(db.String(200), nullable=True)
    levels = db.relationship('UserLevel', backref='user', lazy=True)

    def __repr__(self):
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

    def __repr__(self):
        return f'Level(\'{self.name}\', {self.price})'

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    youtube_link = db.Column(db.String(200), nullable=False)
    questions = db.Column(db.Text, nullable=True)  # JSON with question_id for each question

    def __repr__(self):
        return f'Video(\'{self.youtube_link}\')'

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

    def __repr__(self):
        return f'UserLevel(User: {self.user_id}, Level: {self.level_id})'

class UserVideoProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_level_id = db.Column(db.Integer, db.ForeignKey('user_level.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    is_opened = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)
    # Remove these fields as they'll be tracked in VideoQuestionSubmission
    # correct_words = db.Column(db.Integer, nullable=True)
    # wrong_words = db.Column(db.Integer, nullable=True)
    # percentage = db.Column(db.Float, nullable=True)
    # correct_words_list = db.Column(db.Text, nullable=True)
    # wrong_words_list = db.Column(db.Text, nullable=True)

    # Add unique constraint on user_level_id and video_id
    __table_args__ = (
        db.UniqueConstraint('user_level_id', 'video_id', name='uq_user_level_video'),
    )

    def __repr__(self):
        return f'UserVideoProgress(UserLevel: {self.user_level_id}, Video: {self.video_id}, Opened: {self.is_opened}, Completed: {self.is_completed})'

class VideoQuestionSubmission(db.Model):
    """New model to track multiple question submissions for each video"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    submission_number = db.Column(db.Integer, nullable=False, default=1)  # Track attempt number
    correct_words = db.Column(db.Integer, nullable=False, default=0)
    wrong_words = db.Column(db.Integer, nullable=False, default=0)
    percentage = db.Column(db.Float, nullable=False, default=0.0)
    correct_words_list = db.Column(db.Text, nullable=True)  # JSON list
    wrong_words_list = db.Column(db.Text, nullable=True)    # JSON list
    questions_answers = db.Column(db.Text, nullable=True)   # JSON with question_id and user's answer
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='video_question_submissions')
    level = db.relationship('Level', backref='video_question_submissions')
    video = db.relationship('Video', backref='question_submissions')

    def __repr__(self):
        return f'VideoQuestionSubmission(User: {self.user_id}, Video: {self.video_id}, Attempt: {self.submission_number})'

class ExamResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    correct_words = db.Column(db.Integer, nullable=False)
    wrong_words = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    correct_words_list = db.Column(db.Text, nullable=True)
    wrong_words_list = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'ExamResult(User: {self.user_id}, Level: {self.level_id}, Type: {self.type}, Score: {self.percentage})'