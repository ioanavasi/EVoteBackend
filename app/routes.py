from flask import Blueprint, jsonify, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User
from app import db, login_manager

routes_bp = Blueprint('routes', __name__)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@routes_bp.route('/')
def home():
    return jsonify("Hello, Flask!")

@routes_bp.route('/users')
def get_users():
    try:
        users = User.query.all()
        return jsonify({"users": [user.to_dict() for user in users]}), 200
    except Exception as e:
        return jsonify(str(e)), 400

@routes_bp.route('/register', methods=['POST'])
def register():
    data = request.json

    try:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify("Email already in use"), 400

        new_user = User(
            email=data['email'],
            cnp=data['cnp'],
            hashed_password=generate_password_hash(data['password']),
            first_name=data['first_name'],
            last_name=data['last_name']
        )

        db.session.add(new_user)
        db.session.commit()
        return jsonify("User registered successfully"), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(str(e)), 400

@routes_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    cnp = data['cnp']
    password = data['password']
    
    try:
        # Find the user
        user = User.query.filter_by(cnp=cnp).first()
        
        # Check if password is correct
        if user and check_password_hash(user.hashed_password, password):
            login_user(user)
            return jsonify("Login successful"), 200
        else:
            return jsonify("Invalid credentials"), 401
    except Exception as e:
        return jsonify(str(e)), 400

@routes_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    try:
        logout_user()
        return jsonify("Logout successful"), 200
    except Exception as e:
        return jsonify(str(e)), 400