from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from app.schemas import UserCreate, GetUserId
from app.utils.helpers import format_error_message, get_pagination_params
users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['POST'])
def create_user():
    data = request.get_json()
    try:
        user_data = UserCreate.model_validate(data)
        with db.engine.connect() as connection:
            # Create a transaction that will be committed when the block exits
            with connection.begin():
                # Enable more detailed error reporting
                connection.execute(text("SET client_min_messages TO DEBUG;"))
                
                query = text("""
                SELECT * FROM create_user(:email, :name)
                """)
                
                result = connection.execute(
                    query,
                    {"email": user_data.email, "name": user_data.name}
                )
                
                user_row = result.fetchone()
                if not user_row:
                    return jsonify({"message": "Failed to create user - no row returned"}), 500
                
                print(f"Created user: {user_row}")
                
                user_dict = {
                    "id": str(user_row.id),
                    "email": user_row.email,
                    "name": user_row.name,
                    "created_at": user_row.created_at.isoformat() if user_row.created_at else None
                }
                
                return jsonify({
                    "message": "User created successfully",
                    "user": user_dict
                }), 201
                
    except ValidationError as e:
        error_details = e.errors()
        error_messages = [format_error_message(err) for err in error_details]
        return jsonify({"message": "Validation error", "details": error_messages}), 400
    except IntegrityError as e:
        print(f"Integrity error: {str(e)}")
        return jsonify({"message": "A user with this email already exists"}), 409
    except Exception as e:
        print(f"User creation error: {str(e)}")
        return jsonify({"message": "An unexpected error occurred", "details": str(e)}), 500

@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    page, per_page = get_pagination_params()
    try:
        # Use stored procedure to get all users
        with db.engine.connect() as connection:
            query = text("""
            SELECT * FROM get_all_users()
            """)
            result = connection.execute(query)
            users = []
            for row in result:
                users.append({
                    "id": row.id,
                    "email": row.email,
                    "name": row.name,
                    "created_at": row.created_at
                })
            
            # Manual pagination for a list
            total = len(users)
            pages = (total + per_page - 1) // per_page  # Ceiling division
            start = (page - 1) * per_page
            end = min(start + per_page, total)
            
            paginated_users = users[start:end]
            
            return jsonify({
                "users": paginated_users, 
                "pagination": {
                    "total": total,
                    "pages": pages,
                    "page": page,
                    "per_page": per_page,
                    "has_next": page < pages,
                    "has_prev": page > 1,
                    "next_page": page + 1 if page < pages else None,
                    "prev_page": page - 1 if page > 1 else None
                }
            }), 200
    except Exception as e:
        return jsonify({"message": f"Error fetching users: {str(e)}"}), 500
    


@users_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        user_info = GetUserId(user_id=user_id)
        validated_user_id = str(user_info.user_id)
        
        with db.engine.connect() as connection:
            query = text("""
            SELECT * FROM get_user_by_id(:user_id)
            """)
            result = connection.execute(query, {"user_id": validated_user_id})
            user_row = result.fetchone()
            
            # Check if user exists or if all important fields are None
            if not user_row or user_row.id is None:
                return jsonify({"message": "User not found"}), 404
                
            # Create a dictionary from the SQLAlchemy row
            user_dict = {
                "id": user_row.id,
                "email": user_row.email,
                "name": user_row.name,
                "created_at": user_row.created_at
            }
            
            return jsonify({
                "user": user_dict
            }), 200
        
    except ValidationError as e:
        error_details = e.errors()
        error_messages = [format_error_message(err) for err in error_details]
        return jsonify({"message": "Validation error", "details": error_messages}), 400
    
    except Exception as e:
        return jsonify({"message": f"Error fetching user: {str(e)}"}), 500