from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import User
from app.extensions import db
from sqlalchemy.exc import IntegrityError

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['POST'])
def create_user():
    """Create a new user-waiter"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('email') or not data.get('name'):
        return jsonify({"message": "Email and name are required"}), 400
    
    # Check for email uniqueness
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"message": "Email already exists"}), 409
    
    try:
        new_user = User(
            email=data['email'],
            name=data['name']
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "message": "User created successfully",
            "user": new_user.to_dict()
        }), 201
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "An error occurred while creating the user"}), 500


@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """Get list of all user-waiters"""
    users = User.query.all()
    return jsonify({
        "users": [user.to_dict() for user in users]
    }), 200


@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user-waiter by ID"""
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "user": user.to_dict()
    }), 200