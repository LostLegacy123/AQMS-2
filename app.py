from flask import Flask, render_template, request, jsonify
from datetime import datetime
import hashlib
import json
import os
import pytz

app = Flask(__name__)

# Store the air quality data in a list (in-memory storage)
data = []
max_data_points = 10  # Maximum number of data points to store

# File path for storing user data
user_file_path = 'users.json'

# Timezone configuration (set to your local timezone)
local_tz = pytz.timezone('Asia/Manila')

# Load users from JSON file if it exists
def load_users():
    if os.path.exists(user_file_path):
        with open(user_file_path, 'r') as f:
            return json.load(f)
    return {}

# Save users to JSON file
def save_users(users):
    with open(user_file_path, 'w') as f:
        json.dump(users, f, indent=4)

# Initialize the admin user if not present
def initialize_admin_user():
    admin_username = "admin"
    admin_password_hash = hashlib.sha256("admin".encode()).hexdigest()
    if admin_username not in users:
        users[admin_username] = {
            "password": admin_password_hash,
            "role": "admin",
            "is_active": True
        }
        save_users(users)

# Initialize the user dictionary from the JSON file
users = load_users()
initialize_admin_user()

@app.route('/')
def user():
    return render_template('user.html')

@app.route('/aqi')
def air_quality_index():
    return render_template('aqi.html', data=data)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/practice-button')
def practice_button():
    return render_template('practice button.html')

# Add data to air quality chart with correct timestamp
@app.route('/add_data', methods=['POST'])
def add_data():
    air_quality = request.json.get('airQuality')
    if air_quality is not None:
        # Get the current time with timezone awareness
        current_time = datetime.now(local_tz)
        timestamp = current_time.strftime('%Y-%m-%d %H:%M:%S')

        # Append the data with the correct timestamp
        data.append({'time': timestamp, 'value': int(air_quality)})

        # Limit the number of data points stored
        if len(data) > max_data_points:
            data.pop(0)

        print(f"New data added: {data[-1]}")
        return jsonify({'status': 'success', 'data': data}), 200
    else:
        print("No air quality data received.")
        return jsonify({'status': 'failed', 'message': 'Invalid data'}), 400

@app.route('/get_data', methods=['GET'])
def get_data():
    print(f"Current data: {data}")
    return jsonify(data)

# User authentication: Register and Login
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    
    if not username or not password:
        return jsonify({'status': 'failed', 'message': 'Username and password required'}), 400
    
    if username in users:
        return jsonify({'status': 'failed', 'message': 'User already exists'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    users[username] = {
        "password": hashed_password,
        "role": "user",
        "is_active": True
    }

    # Save users to the JSON file
    save_users(users)

    return jsonify({'status': 'success', 'message': 'User registered successfully'}), 200

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'status': 'failed', 'message': 'Username and password required'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user = users.get(username)

    if user and user["password"] == hashed_password:
        return jsonify({'status': 'success', 'message': 'Login successful'}), 200
    else:
        return jsonify({'status': 'failed', 'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
