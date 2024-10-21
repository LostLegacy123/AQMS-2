from flask import Flask, render_template, request, jsonify
import time
import hashlib

app = Flask(__name__)

# Store the air quality data in a list (in-memory storage)
data = []
max_data_points = 10  # Maximum number of data points to store

# In-memory user store (should be replaced with a database in production)
users = {}

@app.route('/')
def index():
    return render_template('user.html')

@app.route('/aqi')
def air_quality_index():
    return render_template('aqi.html', data=data)

@app.route('/index')
def user():
    return render_template('index.html')

@app.route('/practice-button')
def practice_button():
    return render_template('practice button.html')

@app.route('/add_data', methods=['POST'])
def add_data():
    air_quality = request.json.get('airQuality')
    if air_quality is not None:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        data.append({'time': timestamp, 'value': int(air_quality)})
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
    users[username] = hashed_password

    return jsonify({'status': 'success', 'message': 'User registered successfully'}), 200

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'status': 'failed', 'message': 'Username and password required'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    stored_password = users.get(username)

    if stored_password and stored_password == hashed_password:
        return jsonify({'status': 'success', 'message': 'Login successful'}), 200
    else:
        return jsonify({'status': 'failed', 'message': 'Invalid credentials'}), 401

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
