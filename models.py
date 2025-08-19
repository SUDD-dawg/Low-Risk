from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    overall_experience = db.Column(db.String(50), nullable=False)
    helpful_rating = db.Column(db.String(50), nullable=False)
    suggestions = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), nullable=True)  # 'good' or 'constructive'
    confidence_score = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ai_processed = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'overall_experience': self.overall_experience,
            'helpful_rating': self.helpful_rating,
            'suggestions': self.suggestions,
            'category': self.category,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat(),
            'ai_processed': self.ai_processed
        }

class FeedbackService:
    @staticmethod
    def create_feedback(overall_exp, helpful_rating, suggestions):
        feedback = Feedback(
            overall_experience=overall_exp,
            helpful_rating=helpful_rating,
            suggestions=suggestions
        )
        db.session.add(feedback)
        db.session.commit()
        return feedback
    
    @staticmethod
    def get_all_feedback():
        return Feedback.query.order_by(Feedback.created_at.desc()).all()
    
    @staticmethod
    def get_feedback_by_id(feedback_id):
        return Feedback.query.get(feedback_id)
    
    @staticmethod
    def update_feedback_category(feedback_id, category, confidence_score):
        feedback = Feedback.query.get(feedback_id)
        if feedback:
            feedback.category = category
            feedback.confidence_score = confidence_score
            feedback.ai_processed = True
            db.session.commit()
            return feedback
        return None
    
    @staticmethod
    def get_unprocessed_feedback():
        return Feedback.query.filter_by(ai_processed=False).all()
