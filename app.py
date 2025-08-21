from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from models import db, Feedback, FeedbackService, User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'feedback.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# Home page route - now requires login
@app.route('/')
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

# Enhanced Eligibility page route - GET for displaying form, POST for processing
@app.route('/eligibility', methods=['GET', 'POST'])
def eligibility():
    if request.method == 'POST':
        try:
            # Get form data with validation
            income = float(request.form.get('income', 0))
            loan = float(request.form.get('loan', 0))
            deposit = float(request.form.get('deposit', 0))
            expenses = float(request.form.get('expenses', 0))
            
            # Basic validation matching HTML form
            if income < 0 or income > 1000000:
                return render_template('eligibility-enhanced.html', 
                                     eligible=None,
                                     error="Income must be between $0 and $1,000,000")
            if loan < 0 or loan > 5000000:
                return render_template('eligibility-enhanced.html', 
                                     eligible=None,
                                     error="Loan must be between $0 and $5,000,000")
            if deposit < 0 or deposit > 1000000:
                return render_template('eligibility-enhanced.html', 
                                     eligible=None,
                                     error="Deposit must be between $0 and $1,000,000")
            if expenses < 0 or expenses > 50000:
                return render_template('eligibility-enhanced.html', 
                                     eligible=None,
                                     error="Expenses must be between $0 and $50,000")
            
            # Enhanced calculation
            disposable_income = max(0, income - expenses)
            max_monthly_payment = disposable_income * 0.3
            max_loan = max_monthly_payment * 12 * 5  # 5 year term
            
            # Check eligibility
            is_eligible = (
                loan <= max_loan and 
                deposit >= loan * 0.1 and
                disposable_income > 0
            )
            
            return render_template('eligibility-enhanced.html', 
                                 eligible=is_eligible,
                                 max_loan=round(max_loan, 2))
            
        except ValueError:
            return render_template('eligibility-enhanced.html', 
                                 eligible=None,
                                 error="Please enter valid numbers")
    
    return render_template('eligibility-enhanced.html', eligible=None)

# Risk assessment page route - GET for displaying form, POST for processing
@app.route('/risk', methods=['GET', 'POST'])
def risk():
    if request.method == 'POST':
        # Get form data
        debt = float(request.form.get('debt', 0))
        income = float(request.form.get('income', 1))
        
        # Calculate debt-to-income ratio
        debt_to_income = (debt / income) * 100 if income > 0 else 0
        
        # Determine risk level
        if debt_to_income < 20:
            risk_level = "Low Risk"
        elif debt_to_income < 40:
            risk_level = "Medium Risk"
        else:
            risk_level = "High Risk"
        
        return render_template('risk.html', 
                             risk_level=risk_level, 
                             debt_to_income=round(debt_to_income, 2))
    
    return render_template('risk.html')

# Feedback page route - GET for displaying form, POST for processing
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        # Get form data
        overall_exp = request.form.get('overall_exp')
        helpful_rating = request.form.get('helpful_rating')
        suggestions = request.form.get('suggestions')
        
        # Save feedback to database
        feedback = FeedbackService.create_feedback(overall_exp, helpful_rating, suggestions)
        
        # Simple categorization based on ratings
        if overall_exp in ['Excellent', 'Good'] and helpful_rating in ['Very', 'Good']:
            category = 'good'
            confidence_score = 0.9
        else:
            category = 'constructive'
            confidence_score = 0.8
            
        # Update feedback with category
        FeedbackService.update_feedback_category(feedback.id, category, confidence_score)
        
        return render_template('feedback.html', 
                             submitted=True,
                             overall_exp=overall_exp,
                             helpful_rating=helpful_rating,
                             suggestions=suggestions)
    
    return render_template('feedback.html')

# Admin Dashboard route
@app.route('/dashboard')
def dashboard():
    # Get all feedback categorized
    all_feedback = FeedbackService.get_all_feedback()
    
    # Separate into positive and constructive feedback
    positive_feedback = [f for f in all_feedback if f.category == 'good']
    constructive_feedback = [f for f in all_feedback if f.category == 'constructive']
    
    return render_template('dashboard.html', 
                         positive_feedback=positive_feedback,
                         constructive_feedback=constructive_feedback,
                         total_feedback=len(all_feedback))

# API endpoint for eligibility check (optional)
@app.route('/api/eligibility', methods=['POST'])
def api_eligibility():
    data = request.get_json()
    
    income = float(data.get('income', 0))
    loan = float(data.get('loan', 0))
    deposit = float(data.get('deposit', 0))
    expenses = float(data.get('expenses', 0))
    
    disposable_income = income - expenses
    max_monthly_payment = disposable_income * 0.3
    max_loan = max_monthly_payment * 12 * 5
    
    is_eligible = (
        loan <= max_loan and 
        deposit >= loan * 0.1 and
        disposable_income > 0
    )
    
    return jsonify({
        'eligible': is_eligible,
        'max_loan': round(max_loan, 2),
        'disposable_income': round(disposable_income, 2)
    })

# API endpoint for risk assessment (optional)
@app.route('/api/risk', methods=['POST'])
def api_risk():
    data = request.get_json()
    
    debt = float(data.get('debt', 0))
    income = float(data.get('income', 1))
    
    debt_to_income = (debt / income) * 100 if income > 0 else 0
    
    if debt_to_income < 20:
        risk_level = "Low Risk"
    elif debt_to_income < 40:
        risk_level = "Medium Risk"
    else:
        risk_level = "High Risk"
    
    return jsonify({
        'risk_level': risk_level,
        'debt_to_income': round(debt_to_income, 2)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
