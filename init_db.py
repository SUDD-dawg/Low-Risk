#!/usr/bin/env python3
"""
Script to initialize the database with sample feedback data
"""

from app import app
from models import db, Feedback, FeedbackService

def init_sample_data():
    """Initialize database with sample feedback data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Sample feedback data
        sample_feedback = [
            {
                'overall_experience': 'Excellent',
                'helpful_rating': 'Very',
                'suggestions': 'The eligibility calculator was very helpful and easy to use. The interface is intuitive and the results were accurate.'
            },
            {
                'overall_experience': 'Good',
                'helpful_rating': 'Good',
                'suggestions': 'The risk assessment tool is useful, but could benefit from more detailed explanations of the risk factors.'
            },
            {
                'overall_experience': 'Average',
                'helpful_rating': 'Good',
                'suggestions': 'The feedback form is straightforward, but the loading time could be improved.'
            },
            {
                'overall_experience': 'Poor',
                'helpful_rating': 'Average',
                'suggestions': 'The website needs significant improvements in terms of user experience and design. The navigation is confusing and the forms are too long.'
            },
            {
                'overall_experience': 'Excellent',
                'helpful_rating': 'Very',
                'suggestions': 'Absolutely love this service! The risk calculator helped me understand my financial situation better. Keep up the great work!'
            }
        ]
        
        # Add sample feedback
        for feedback_data in sample_feedback:
            feedback = FeedbackService.create_feedback(
                feedback_data['overall_experience'],
                feedback_data['helpful_rating'],
                feedback_data['suggestions']
            )
            
            # Categorize feedback
            if feedback_data['overall_experience'] in ['Excellent', 'Good'] and feedback_data['helpful_rating'] in ['Very', 'Good']:
                category = 'good'
                confidence_score = 0.9
            else:
                category = 'constructive'
                confidence_score = 0.8
                
            FeedbackService.update_feedback_category(feedback.id, category, confidence_score)
        
        print("✅ Database initialized with sample feedback data!")
        print("📊 Admin Dashboard available at: http://localhost:8000/dashboard")
        print("📝 Feedback form available at: http://localhost:8000/feedback")

if __name__ == "__main__":
    init_sample_data()
