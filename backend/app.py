from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import bcrypt
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
jwt = JWTManager(app)

# In-memory storage (replace with database in production)
users = [
    {
        "id": "1",
        "name": "John Doe", 
        "email": "john@example.com",
        "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "createdAt": "2024-01-01T00:00:00Z"
    },
    {
        "id": "2",
        "name": "Jane Smith", 
        "email": "jane@example.com",
        "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "createdAt": "2024-01-01T00:00:00Z"
    }
]

user_settings = {}

@app.route('/')
def home():
    return jsonify({"message": "Flask backend is running!"})

# Authentication routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('name') or not data.get('email') or not data.get('password'):
            return jsonify({"message": "All fields are required"}), 400
        
        # Check if user already exists
        if any(user['email'] == data['email'] for user in users):
            return jsonify({"message": "User already exists"}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create new user
        new_user = {
            "id": str(uuid.uuid4()),
            "name": data['name'],
            "email": data['email'],
            "password": hashed_password,
            "createdAt": datetime.utcnow().isoformat() + 'Z'
        }
        
        users.append(new_user)
        
        # Create access token
        access_token = create_access_token(identity=new_user['id'])
        
        return jsonify({
            "message": "User created successfully",
            "token": access_token,
            "user": {
                "id": new_user['id'],
                "name": new_user['name'],
                "email": new_user['email'],
                "createdAt": new_user['createdAt']
            }
        }), 201
        
    except Exception as e:
        return jsonify({"message": "Registration failed", "error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('email') or not data.get('password'):
            return jsonify({"message": "Email and password are required"}), 400
        
        # Find user
        user = next((u for u in users if u['email'] == data['email']), None)
        if not user:
            return jsonify({"message": "Invalid credentials"}), 401
        
        # Check password
        if not bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({"message": "Invalid credentials"}), 401
        
        # Create access token
        access_token = create_access_token(identity=user['id'])
        
        return jsonify({
            "message": "Login successful",
            "token": access_token,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "createdAt": user['createdAt']
            }
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Login failed", "error": str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        user = next((u for u in users if u['id'] == user_id), None)
        
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        return jsonify({
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "createdAt": user['createdAt']
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Failed to get user", "error": str(e)}), 500

@app.route('/api/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Update user data
        if data.get('name'):
            user['name'] = data['name']
        if data.get('email'):
            # Check if email is already taken by another user
            if any(u['email'] == data['email'] and u['id'] != user_id for u in users):
                return jsonify({"message": "Email already taken"}), 400
            user['email'] = data['email']
        
        return jsonify({
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "createdAt": user['createdAt']
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Profile update failed", "error": str(e)}), 500

@app.route('/api/auth/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('currentPassword') or not data.get('newPassword'):
            return jsonify({"message": "Current and new password are required"}), 400
        
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # Check current password
        if not bcrypt.checkpw(data['currentPassword'].encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({"message": "Current password is incorrect"}), 401
        
        # Hash new password
        user['password'] = bcrypt.hashpw(data['newPassword'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        return jsonify({"message": "Password changed successfully"}), 200
        
    except Exception as e:
        return jsonify({"message": "Password change failed", "error": str(e)}), 500

@app.route('/api/auth/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    try:
        user_id = get_jwt_identity()
        
        # Remove user from users list
        global users
        users = [u for u in users if u['id'] != user_id]
        
        # Remove user settings
        if user_id in user_settings:
            del user_settings[user_id]
        
        return jsonify({"message": "Account deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"message": "Account deletion failed", "error": str(e)}), 500

# User settings routes
@app.route('/api/user/settings', methods=['GET'])
@jwt_required()
def get_user_settings():
    try:
        user_id = get_jwt_identity()
        
        # Default settings
        default_settings = {
            "notifications": {
                "email": True,
                "push": False,
                "sms": False
            },
            "privacy": {
                "profileVisible": True,
                "showEmail": False,
                "allowMessages": True
            },
            "appearance": {
                "theme": "dark",
                "language": "en"
            }
        }
        
        settings = user_settings.get(user_id, default_settings)
        return jsonify(settings), 200
        
    except Exception as e:
        return jsonify({"message": "Failed to get settings", "error": str(e)}), 500

@app.route('/api/user/settings', methods=['PUT'])
@jwt_required()
def update_user_settings():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user_settings[user_id] = data
        
        return jsonify({"message": "Settings updated successfully"}), 200
        
    except Exception as e:
        return jsonify({"message": "Settings update failed", "error": str(e)}), 500

# Users management routes (for dashboard)
@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        # Return users without passwords
        safe_users = [
            {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "createdAt": user['createdAt']
            }
            for user in users
        ]
        return jsonify(safe_users), 200
        
    except Exception as e:
        return jsonify({"message": "Failed to get users", "error": str(e)}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        return jsonify({
            "id": user['id'],
            "name": user['name'],
            "email": user['email'],
            "createdAt": user['createdAt']
        }), 200
        
    except Exception as e:
        return jsonify({"message": "Failed to get user", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)