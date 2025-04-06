from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Product, OrderProduct, Order
from app.extensions import db
from datetime import datetime
from sqlalchemy import func, desc
from sqlalchemy.exc import IntegrityError
from app.schemas import DateRangeParams
from app.utils.helpers import format_error_message
from datetime import date, datetime

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/products', methods=['GET'])
@jwt_required()
def get_product_sales_report():
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    date_params = {}
    if request.args.get('start_date'):
        date_params['start_date'] = request.args.get('start_date')
    if request.args.get('end_date'):
        date_params['end_date'] = request.args.get('end_date')
    
    # Validate date parameters
    try:
        validated_params = DateRangeParams(**date_params)
    
    
        today = datetime.now().date()
        
        if validated_params.start_date is None:
            first_day_of_month = date(today.year, today.month, 1)
            validated_params.start_date = first_day_of_month.strftime('%Y-%m-%d')
        
        if validated_params.end_date is None:
            validated_params.end_date = today.strftime('%Y-%m-%d')
        
        start_date = datetime.strptime(validated_params.start_date, '%Y-%m-%d')
        
        end_date = datetime.strptime(validated_params.end_date, '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59)
        
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
        
        query = query.filter(Order.created_at >= start_date)
        query = query.filter(Order.created_at <= end_date)
        
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
                "start_date": validated_params.start_date,
                "end_date": validated_params.end_date,
                "products": report_data
            }
        }), 200
    except Exception as e:
        error_details = e.errors()
        error_messages = [format_error_message(err) for err in error_details]
        return jsonify({"message": "Validation error", "details": error_messages}), 400
    except IntegrityError as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Unexpected error: {str(e)}"}), 500