from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Order, Product, OrderProduct
from app.extensions import db
from sqlalchemy.exc import IntegrityError

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order with products"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    if not data.get('customer_name'):
        return jsonify({"message": "Customer name is required"}), 400
    
    if not data.get('products') or not isinstance(data['products'], list) or len(data['products']) == 0:
        return jsonify({"message": "At least one product is required"}), 400
    
    # Check if user exists
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    
    try:
        # Calculate total price
        total_price = 0
        order_products = []
        
        # Create/update products and prepare order products
        for product_data in data['products']:
            if not product_data.get('name') or not product_data.get('price') or not product_data.get('quantity'):
                return jsonify({"message": "Each product must have a name, price, and quantity"}), 400
            
            # Check if product exists, otherwise create it
            product = Product.query.filter_by(name=product_data['name']).first()
            if not product:
                product = Product(
                    name=product_data['name'],
                    price=product_data['price']
                )
                db.session.add(product)
                db.session.flush()  # To get the ID without committing
            
            # Create order product
            order_product = OrderProduct(
                product_id=product.id,
                quantity=product_data['quantity'],
                unit_price=product_data['price']
            )
            order_products.append(order_product)
            
            # Add to total price
            total_price += product_data['price'] * product_data['quantity']
        
        # Create order
        new_order = Order(
            user_id=current_user_id,
            customer_name=data['customer_name'],
            total_price=total_price
        )
        
        db.session.add(new_order)
        db.session.flush()  # To get the order ID
        
        # Associate products with order
        for order_product in order_products:
            order_product.order_id = new_order.id
            db.session.add(order_product)
        
        db.session.commit()
        
        return jsonify({
            "message": "Order created successfully",
            "order": new_order.to_dict()
        }), 201
    
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred while creating the order: {str(e)}"}), 500


@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Get all orders for the authenticated user"""
    current_user_id = get_jwt_identity()
    
    # Optional query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limit per_page to avoid performance issues
    if per_page > 100:
        per_page = 100
    
    orders = Order.query.filter_by(user_id=current_user_id).order_by(
        Order.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "orders": [order.to_dict() for order in orders.items],
        "total": orders.total,
        "pages": orders.pages,
        "current_page": page
    }), 200


@orders_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get order details by ID"""
    current_user_id = get_jwt_identity()
    
    order = Order.query.filter_by(id=order_id, user_id=current_user_id).first()
    
    if not order:
        return jsonify({"message": "Order not found"}), 404
    
    return jsonify({
        "order": order.to_dict()
    }), 200