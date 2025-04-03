from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Product, OrderProduct, Order
from app.extensions import db
from datetime import datetime
from sqlalchemy import func, desc

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/products', methods=['GET'])
@jwt_required()
def get_product_sales_report():
    """Generate a report of sold products within a date range"""
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Validate date format
    try:
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            # Make end_date inclusive by setting it to the end of the day
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Build the base query to get orders from the current user
    query = db.session.query(
        Product.name.label('product_name'),
        func.sum(OrderProduct.quantity).label('total_quantity'),
        func.sum(OrderProduct.quantity * OrderProduct.unit_price).label('total_price')
    ).join(
        OrderProduct, Product.id == OrderProduct.product_id
    ).join(
        Order, OrderProduct.order_id == Order.id
    ).filter(
        Order.user_id == current_user_id
    )
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Order.created_at >= start_date)
    if end_date:
        query = query.filter(Order.created_at <= end_date)
    
    # Group by product and order by total quantity sold (descending)
    results = query.group_by(
        Product.name
    ).order_by(
        func.sum(OrderProduct.quantity).desc()
    ).all()
    
    # Format results
    report_data = []
    for product_name, total_quantity, total_price in results:
        report_data.append({
            "product_name": product_name,
            "total_quantity": total_quantity,
            "total_price": float(total_price)
        })
    
    return jsonify({
        "report": {
            "start_date": start_date.strftime('%Y-%m-%d') if start_date else None,
            "end_date": end_date.strftime('%Y-%m-%d') if end_date else None,
            "products": report_data
        }
    }), 200