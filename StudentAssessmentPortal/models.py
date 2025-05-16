from datetime import datetime
from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    year_of_passing = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with Assessment
    assessments = db.relationship('Assessment', backref='user', lazy=True)
    
    def __repr__(self):
        return f"User('{self.name}', '{self.email}')"


class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_type = db.Column(db.String(50), nullable=False)  # 'initial', 'quant', 'verbal', 'reasoning'
    score = db.Column(db.Integer, nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    date_taken = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    
    # Store topic-wise performance data
    topics_data = db.Column(db.Text, nullable=True)  # Will store JSON data of topic performance
    
    def __repr__(self):
        return f"Assessment('{self.assessment_type}', '{self.score}/{self.max_score}')"


class TopicPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'quant', 'verbal', 'reasoning'
    topic = db.Column(db.String(100), nullable=False)
    correct = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"TopicPerformance('{self.category}', '{self.topic}', '{self.correct}/{self.total}')"
