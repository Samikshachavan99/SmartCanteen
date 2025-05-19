from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import qrcode
import os
import urllib.parse

app = Flask(__name__)

# MySQL database config with encoded password
db_user = 'root'
db_password = urllib.parse.quote_plus('shreya@01')  # URL encode the password
db_host = 'localhost'
db_name = 'smart_canteen'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    food_item = db.Column(db.String(100))
    time_slot = db.Column(db.String(100))

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Handle order submissions
@app.route('/order', methods=['GET', 'POST'])  # Added GET method
def order():
    if request.method == 'GET':
        # Handle GET requests to /order by redirecting to the homepage
        return redirect(url_for('index'))
        
    # For POST requests
    try:
        # Debug output to see what's in the form data
        print("Form data received:", request.form)
        
        # Check if required fields exist
        if 'name' not in request.form or 'meal' not in request.form:
            return "Missing required form fields. Please go back and fill all fields.", 400
            
        # Get form data with proper error handling
        student_name = request.form.get('name', '')
        food_item = request.form.get('meal', '')
        time_slot = request.form.get('timeSlot', 'Default Time')
        
        # Validate data
        if not student_name or not food_item:
            return "Name and meal selection are required. Please go back and try again.", 400
        
        # Save order to database
        new_order = Order(student_name=student_name, food_item=food_item, time_slot=time_slot)
        db.session.add(new_order)
        db.session.commit()
        
        # Generate QR Code
        qr_data = f"{student_name}-{food_item}-{time_slot}"
        qr = qrcode.make(qr_data)
        qr_filename = f"{student_name}_{food_item}.png"
        qr_path = f"static/qr_codes/{qr_filename}"
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        qr.save(qr_path)
        
        return render_template('order_success.html', qr_filename=qr_filename)
        
    except Exception as e:
        print(f"Error processing order: {e}")
        return f"An error occurred while processing your order: {e}", 500

# Debugging route to test database connection
@app.route('/test-db')
def test_db():
    try:
        # Try a simple database query
        test = db.session.execute(db.select(Order).limit(1)).all()
        return "Database connection successful!"
    except Exception as e:
        return f"Database error: {str(e)}", 500

# Add a route to see all orders (for testing)
@app.route('/orders')
def view_orders():
    try:
        orders = db.session.execute(db.select(Order)).scalars().all()
        result = "<h1>All Orders</h1><ul>"
        for order in orders:
            result += f"<li>ID: {order.id}, Name: {order.student_name}, Meal: {order.food_item}, Time: {order.time_slot}</li>"
        result += "</ul>"
        return result
    except Exception as e:
        return f"Error retrieving orders: {e}", 500

if __name__ == '__main__':
    # Create tables before running the app
    with app.app_context():
        db.create_all()
    app.run(debug=True)