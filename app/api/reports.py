from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app.schemas import DateRangeParams
from app.utils.helpers import format_error_message
from datetime import date, datetime
from pydantic import ValidationError

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/products', methods=['GET'])
@jwt_required()
def get_product_sales_report():
    current_user_id = get_jwt_identity()
    try:
        validated_params = DateRangeParams(**request.args)
        today = datetime.now().date()
        
        if validated_params.start_date is None:
            first_day_of_month = date(today.year, today.month, 1)
            validated_params.start_date = first_day_of_month.strftime('%Y-%m-%d')
        
        if validated_params.end_date is None:
            validated_params.end_date = today.strftime('%Y-%m-%d')
            
        start_date = datetime.strptime(validated_params.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(validated_params.end_date, '%Y-%m-%d')
        end_date = end_date.replace(hour=23, minute=59, second=59)
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)  # Default page is 1
        page_size = request.args.get('page_size', 10, type=int)  # Default page size is 10
        
        # Calculate OFFSET for pagination
        offset = (page - 1) * page_size
        
        # Use the stored procedure for data
        with db.engine.connect() as connection:
            # First, get the total count
            count_query = text("""
                SELECT COUNT(*) FROM get_product_sales_report(:user_id, :start_date, :end_date)
            """)
            
            total_records = connection.execute(
                count_query,
                {
                    "user_id": current_user_id,
                    "start_date": start_date,
                    "end_date": end_date
                }
            ).scalar()
            
            # Then get the paginated data
            data_query = text("""
                SELECT * FROM get_product_sales_report(:user_id, :start_date, :end_date)
                LIMIT :limit OFFSET :offset
            """)
            
            result = connection.execute(
                data_query,
                {
                    "user_id": current_user_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "limit": page_size,
                    "offset": offset
                }
            )
            
            # Format results
            report_data = []
            for row in result:
                report_data.append({
                    "product_name": row.product_name,
                    "total_quantity": row.total_quantity,
                    "total_price": float(round(row.total_price, 2))
                })
            
            # Calculate total pages
            total_pages = (total_records + page_size - 1) // page_size if total_records else 0
            
            return jsonify({
                "report": {
                    "start_date": validated_params.start_date,
                    "end_date": validated_params.end_date,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "total_records": total_records,
                    "products": report_data
                }
            }), 200
            
    except ValidationError as e:
        error_details = e.errors()
        error_messages = [format_error_message(err) for err in error_details]
        return jsonify({"message": "Validation error", "details": error_messages}), 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500