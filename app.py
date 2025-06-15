from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 300,
    'pool_pre_ping': True
}

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.String(7), nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

@app.context_processor
def inject_utilities():
    return {
        'datetime': datetime,
        'max': max,
        'min': min
    }

@app.route('/')
def index():
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    
    categories = db.session.query(
        Expense.category, 
        db.func.sum(Expense.amount).label('total')
    ).group_by(Expense.category).all()
    
    category_names = [str(c[0]) for c in categories]
    category_totals = [float(c[1]) for c in categories]
    
    current_month = datetime.now().strftime('%Y-%m')
    current_budget = Budget.query.filter_by(month=current_month).first()
    
    total_spent = db.session.query(db.func.sum(Expense.amount)).filter(
        db.func.strftime('%Y-%m', Expense.date) == current_month
    ).scalar() or 0
    
    budget_percentage = 0
    if current_budget and current_budget.amount > 0:
        budget_percentage = min(100, round((total_spent / current_budget.amount) * 100, 2))
    
    return render_template('index.html',
                        expenses=expenses,
                        category_names=category_names,
                        category_totals=category_totals,
                        current_month=current_month,
                        current_budget=current_budget,
                        total_spent=total_spent,
                        budget_percentage=budget_percentage)

@app.route('/add', methods=['POST'])
def add_expense():
    try:
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form.get('description', '')
        
        if amount <= 0:
            flash('Amount must be greater than 0', 'danger')
            return redirect(url_for('index'))
            
        new_expense = Expense(
            date=date,
            amount=amount,
            category=category,
            description=description
        )
        
        db.session.add(new_expense)
        db.session.commit()
        flash('Expense added successfully!', 'success')
    except ValueError:
        flash('Invalid amount or date format', 'danger')
    except Exception as e:
        flash(f'Error adding expense: {str(e)}', 'danger')
    
    return redirect(url_for('index'))

@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    try:
        expense = Expense.query.get_or_404(expense_id)
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting expense: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.route('/set-budget', methods=['POST'])
def set_budget():
    try:
        month = request.form['month']
        amount = float(request.form['amount'])
        
        if amount <= 0:
            flash('Budget amount must be greater than 0', 'danger')
            return redirect(url_for('index'))
            
        budget = Budget.query.filter_by(month=month).first()
        if budget:
            budget.amount = amount
        else:
            budget = Budget(month=month, amount=amount)
            db.session.add(budget)
        
        db.session.commit()
        flash('Budget updated successfully', 'success')
    except Exception as e:
        flash(f'Error setting budget: {str(e)}', 'danger')
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)