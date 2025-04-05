from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Order, Product, OrderProduct
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError
from app.schemas import OrderCreate

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    current_user_id = get_jwt_identity()
    
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"message": "No JSON data provided"}), 400
    
    try:
        order_data = OrderCreate.model_validate(data)
        
        total_price = 0
        order_products = []
        
        # Create/update products and prepare order products
        for product_data in order_data.products:
            # Check if product exists, otherwise create it
            product = Product.query.filter_by(name=product_data.name).first()
            if not product:
                product = Product(
                    name=product_data.name,
                    price=product_data.price
                )
                db.session.add(product)
                db.session.flush()
            if not product.price:
                order_product = OrderProduct(
                    product_id=product.id,
                    quantity=product_data.quantity,
                    unit_price=product_data.price
                )
                order_products.append(order_product)
                total_price += product_data.price * product_data.quantity
            else:
                order_product = OrderProduct(
                    product_id=product.id,
                    quantity=product_data.quantity,
                    unit_price=product.price
                )
                order_products.append(order_product)
                total_price += product.price * product_data.quantity
        
        new_order = Order(
            user_id=current_user_id,
            customer_name=order_data.customer_name,
            total_price=total_price
        )
        
        db.session.add(new_order)
        db.session.flush() 
        
        for order_product in order_products:
            order_product.order_id = new_order.id
            db.session.add(order_product)
        
        db.session.commit()
        
        return jsonify({
            "message": "Order created successfully",
            "order": new_order.to_dict()
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
    
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({
            "message": f"Database error: {str(e)}"
        }), 500
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "message": f"Unexpected error: {str(e)}"
        }), 500