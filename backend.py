from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import mysql.connector
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import uuid
from functools import wraps
import requests
import json

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx'}

jwt = JWTManager(app)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'fajao_user',
    'password': 'securepassword',
    'database': 'fajao_exam_bank_db'
}

# InfoSend API configuration
import os

secret_key = os.getenv("INTASEND_SECRET_KEY")

INTASEND_PUBLIC_KEY = 'ISPubKey_live_e976a10a-3749-4b24-906e-c36d5ef62c84'
INTASEND_SECRET_KEY = secret_key
INTASEND_API_URL = 'https://payment.intasend.com/api/v1/payment/'

def get_db_connection():
    return mysql.connector.connect(**db_config)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create upload directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Premium subscription required decorator
def premium_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT is_premium FROM users WHERE id = %s", (current_user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user or not user['is_premium']:
            return jsonify({'message': 'Premium subscription required'}), 403
            
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not name or not email or not password:
            return jsonify({'message': 'Missing required fields'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'message': 'User already exists'}), 409
            
        # Create new user (in production, hash the password)
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, is_premium) VALUES (%s, %s, %s, %s)",
            (name, email, password, False)
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        cursor.close()
        conn.close()
        
        # Create access token
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'message': 'User created successfully',
            'token': access_token,
            'user': {
                'id': user_id,
                'name': name,
                'email': email,
                'is_premium': False
            }
        }), 201
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'message': 'Missing email or password'}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE email = %s AND password_hash = %s", (email, password))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 401
            
        # Create access token
        access_token = create_access_token(identity=user['id'])
        
        return jsonify({
            'message': 'Login successful',
            'token': access_token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'is_premium': bool(user['is_premium'])
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, name, email, is_premium FROM users WHERE id = %s", (current_user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
            
        return jsonify({
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'is_premium': bool(user['is_premium'])
        }), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/exams', methods=['GET'])
def get_exams():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get search parameters from request
        search_query = request.args.get('q')
        subject = request.args.get('subject')
        form_level = request.args.get('form')
        exam_type = request.args.get('type')
        
        # Build query based on filters
        query = """
            SELECT e.*, u.name as uploaded_by_name 
            FROM exams e 
            JOIN users u ON e.uploaded_by = u.id 
            WHERE 1=1
        """
        params = []
        
        if search_query:
            query += " AND (e.title LIKE %s OR e.subject LIKE %s)"
            params.extend([f'%{search_query}%', f'%{search_query}%'])
        
        if subject and subject != 'All Subjects':
            query += " AND e.subject = %s"
            params.append(subject)
        
        if form_level and form_level != 'All Forms':
            query += " AND e.form_level = %s"
            params.append(form_level)
            
        if exam_type and exam_type != 'All Types':
            query += " AND e.exam_type = %s"
            params.append(exam_type)
        
        query += " ORDER BY e.upload_date DESC"
        
        cursor.execute(query, params)
        exams = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({'exams': exams}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/exams/upload', methods=['POST'])
@jwt_required()
def upload_exam():
    try:
        current_user_id = get_jwt_identity()
        
        # Check if file is included
        if 'file' not in request.files:
            return jsonify({'message': 'No file uploaded'}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'message': 'No file selected'}), 400
            
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            
            # Get other form data
            title = request.form.get('title')
            subject = request.form.get('subject')
            form_level = request.form.get('form_level')
            exam_type = request.form.get('exam_type')
            is_premium = request.form.get('is_premium', 'false').lower() == 'true'
            
            # Get file size and type
            file_size = os.path.getsize(filepath)
            file_type = filename.rsplit('.', 1)[1].upper() if '.' in filename else 'UNKNOWN'
            
            # Save to database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO exams (title, subject, form_level, exam_type, is_premium, 
                                 filename, file_size, file_type, uploaded_by, upload_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (title, subject, form_level, exam_type, is_premium, 
                                 unique_filename, file_size, file_type, current_user_id))
            conn.commit()
            
            exam_id = cursor.lastrowid
            
            cursor.close()
            conn.close()
            
            return jsonify({'message': 'File uploaded successfully', 'exam_id': exam_id}), 200
        
        return jsonify({'message': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/exams/download/<int:exam_id>', methods=['GET'])
@jwt_required()
def download_exam(exam_id):
    try:
        current_user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get exam details
        cursor.execute("SELECT * FROM exams WHERE id = %s", (exam_id,))
        exam = cursor.fetchone()
        
        if not exam:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Exam not found'}), 404
            
        # Check if user has access to premium content
        if exam['is_premium']:
            cursor.execute("SELECT is_premium FROM users WHERE id = %s", (current_user_id,))
            user = cursor.fetchone()
            
            if not user or not user['is_premium']:
                cursor.close()
                conn.close()
                return jsonify({'message': 'Premium subscription required'}), 403
        
        # Update download count
        cursor.execute("UPDATE exams SET download_count = download_count + 1 WHERE id = %s", (exam_id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], exam['filename'])
        
        if not os.path.exists(filepath):
            return jsonify({'message': 'File not found'}), 404
            
        return send_file(filepath, as_attachment=True, download_name=exam['title'] + '.' + exam['filename'].split('.')[-1])
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/api/payments/subscribe', methods=['POST'])
@jwt_required()
def process_subscription():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        plan = data.get('plan')
        payment_method = data.get('method')
        phone_number = data.get('phone_number')  # For M-Pesa
        
        if plan not in ['monthly', 'annual']:
            return jsonify({'message': 'Invalid plan'}), 400
            
        # Determine amount based on plan
        amount = 500 if plan == 'monthly' else 5000  # KSh 500 monthly, KSh 5000 annually
        
        # Process payment with InfoSend
        payment_success = process_intasend_payment(amount, payment_method, phone_number)
        
        if not payment_success:
            return jsonify({'message': 'Payment failed'}), 400
            
        # Update user premium status
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Set premium expiry date (1 month for monthly, 1 year for annual)
        expiry_interval = 1 if plan == 'monthly' else 12
        
        cursor.execute(
            "UPDATE users SET is_premium = 1, premium_expiry = DATE_ADD(NOW(), INTERVAL %s MONTH) WHERE id = %s",
            (expiry_interval, current_user_id)
        )
        conn.commit()
        
        # Record payment in database
        cursor.execute(
            "INSERT INTO payments (user_id, plan_type, amount, payment_method, payment_status) VALUES (%s, %s, %s, %s, %s)",
            (current_user_id, plan, amount, payment_method, 'completed')
        )
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Subscription successful'}), 200
        
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def process_intasend_payment(amount, method, phone_number=None):
    """
    Process payment with InfoSend API
    This is a simplified implementation - you'll need to adapt it to the actual InfoSend API
    """
    try:
        # Prepare payment data based on method
        payment_data = {
            'amount': amount,
            'currency': 'KES',
            'method': method,
            'public_key': INTASEND_PUBLIC_KEY
        }
        
        if method == 'mpesa' and phone_number:
            payment_data['phone_number'] = phone_number
        
        # Make API request to InfoSend
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {INTASEND_SECRET_KEY}'
        }
        
        # This is a mock implementation - replace with actual InfoSend API call
        response = requests.post(INTASEND_API_URL, json=payment_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('success', False)
        else:
            print(f"Payment failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        return False

if __name__ == '__main__':
    app.run(debug=True, port=5000)