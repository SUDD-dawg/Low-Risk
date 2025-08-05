from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# Home page route
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

# Eligibility page route - GET for displaying form, POST for processing
@app.route('/eligibility', methods=['GET', 'POST'])
def eligibility():
    if request.method == 'POST':
        # Get form data
        income = float(request.form.get('income', 0))
        loan = float(request.form.get('loan', 0))
        deposit = float(request.form.get('deposit', 0))
        expenses = float(request.form.get('expenses', 0))
        
        # Simple eligibility calculation
        disposable_income = income - expenses
        max_loan = disposable_income * 12 * 0.3  # 30% of annual disposable income
        
        is_eligible = loan <= max_loan and deposit >= loan * 0.1
        
        return render_template('eligibility.html', 
                             eligible=is_eligible, 
                             max_loan=round(max_loan, 2))
    
    return render_template('eligibility.html')

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
        
        # Here you would typically save to database
        # For now, we'll just acknowledge submission
        return render_template('feedback.html', 
                             submitted=True,
                             overall_exp=overall_exp,
                             helpful_rating=helpful_rating,
                             suggestions=suggestions)
    
    return render_template('feedback.html')

# API endpoint for eligibility check (optional)
@app.route('/api/eligibility', methods=['POST'])
def api_eligibility():
    data = request.get_json()
    
    income = float(data.get('income', 0))
    loan = float(data.get('loan', 0))
    deposit = float(data.get('deposit', 0))
    expenses = float(data.get('expenses', 0))
    
    disposable_income = income - expenses
    max_loan = disposable_income * 12 * 0.3
    
    is_eligible = loan <= max_loan and deposit >= loan * 0.1
    
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
