from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import User
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from app.schemas import UserCreate

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['POST'])
def create_user():
    data = request.get_json()
    
    user_data = UserCreate.model_validate(data)
    try:
        new_user = User(
            email=user_data['email'],
            name=user_data['name']
        )
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            "message": "User created successfully",
            "user": new_user.to_dict()
        }), 201
    
    except ValidationError as e:
        errors = []
        for error in e.errors():
            error_location = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": error_location,
                "message": error["msg"]
            })
        
        return jsonify({
            "message": "Validation error",
            "errors": errors
        }), 400
    
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "An error occurred while creating the user"}), 500


@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    return jsonify({
        "users": [user.to_dict() for user in users]
    }), 200


@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    return jsonify({
        "user": user.to_dict()
    }), 200