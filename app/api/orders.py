from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from pydantic import ValidationError
from app.schemas import OrderCreate, OrderList, GetOrderId
from app.utils.helpers import format_error_message
from app.utils.helpers import get_pagination_params
from app.utils.db_utils import TransactionManager
import logging

logger = logging.getLogger(__name__)
orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order_by_id(order_id):
    current_user_id = get_jwt_identity()
    
    try:
        # Validate order ID
        validated_id = GetOrderId(order_id=order_id)
        
        # Call stored procedure to get order details
        with db.engine.connect() as connection:
            # Get order details
            query = text("""
            SELECT * FROM get_order_byId(:order_id, :user_id)
            """)
            
            result = connection.execute(
                query,
                {
                    "order_id": validated_id.order_id,
                    "user_id": current_user_id
                }
            )
            
            order_row = result.fetchone()
            if not order_row:
                return jsonify({"message": "Order not found"}), 404
                
            order = {
                "id": order_row.id,
                "user_id": order_row.user_id,
                "customer_name": order_row.customer_name,
                "total_price": float(order_row.total_price) if order_row.total_price else 0.0,
                "created_at": order_row.created_at,
                "products": []
            }
            
            # Get products for this order
            query = text("""
            SELECT * FROM get_order_products_by_ids(:order_ids_csv)
            """)

            products_result = connection.execute(query, {"order_ids_csv": order["id"]})
            
            for prod_row in products_result:
                order["products"].append({
                    "id": prod_row.product_id,
                    "name": prod_row.product_name,
                    "quantity": prod_row.quantity,
                    "unit_price": float(prod_row.unit_price) if prod_row.unit_price else 0.0
                })
                
            return jsonify({"order": order}), 200
            
    except ValidationError as e:
        error_details = e.errors()
        error_messages = [format_error_message(err) for err in error_details]
        return jsonify({"message": "Validation error", "details": error_messages}), 400
        
    except IntegrityError as e:
        logger.error(f"Database integrity error: {str(e)}", exc_info=True)
        return jsonify({
            "message": "A database constraint was violated"
        }), 400
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}", exc_info=True)
        return jsonify({
            "message": "A database error occurred"
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            "message": "An unexpected error occurred"
        }), 500
    

@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    current_user_id = get_jwt_identity()
    page, per_page = get_pagination_params()
    
    try:
        validated_params = OrderList(**request.args)
        
        # Call stored procedure for orders
        with db.engine.connect() as connection:
            # Get all orders without pagination from database
            query = text("""
            SELECT * FROM get_user_orders(
                :user_id, 
                :customer_name, 
                :start_date, 
                :end_date
            )
            """)
            
            result = connection.execute(
                query,
                {
                    "user_id": current_user_id,
                    "customer_name": validated_params.customer_name,
                    "start_date": validated_params.start_date,
                    "end_date": validated_params.end_date
                }
            )
            
            all_orders = []
            for row in result:
                all_orders.append({
                    "id": row.id,
                    "user_id": row.user_id,
                    "customer_name": row.customer_name,
                    "total_price": float(row.total_price) if row.total_price else 0.0,
                    "created_at": row.created_at
                })
            
            # Calculate pagination in Python
            total_count = len(all_orders)
            total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 0
            
            # Apply pagination in Python
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_orders = all_orders[start_idx:end_idx] if all_orders else []
            
            # Extract order IDs for product lookup
            order_ids = [order["id"] for order in paginated_orders]
            
            # Use the paginated orders directly
            orders = paginated_orders.copy()
            
            # Initialize empty products list for each order
            for order in orders:
                order["products"] = []
            
            if order_ids:
                products = []
                order_ids_csv = ','.join(order_ids)

                # Call the function with the single string parameter
                query = text(f"""
                SELECT * FROM get_order_products_by_ids(:order_ids_csv)
                """)

                products_result = connection.execute(query, {"order_ids_csv": order_ids_csv})
                
                order_products_map = {}
                for prod_row in products_result:
                    if prod_row.order_id not in order_products_map:
                        order_products_map[prod_row.order_id] = []
                    
                    order_products_map[prod_row.order_id].append({
                        "id": prod_row.product_id,
                        "name": prod_row.product_name,
                        "quantity": prod_row.quantity,
                        "unit_price": float(prod_row.unit_price) if prod_row.unit_price else 0.0
                    })
                
                # Add products to their respective orders
                for order in orders:
                    if order["id"] in order_products_map:
                        order["products"] = order_products_map[order["id"]]
        return jsonify({
            "orders": orders,
            "pagination": {
                "total": total_count,
                "pages": total_pages,
                "page": page,
                "per_page": per_page,
                "has_next": page < total_pages,
                "has_prev": page > 1,
                "next_page": page + 1 if page < total_pages else None,
                "prev_page": page - 1 if page > 1 else None
            }
        }), 200
        
        
    except ValidationError as e:
        error_details = e.errors()
        error_messages = [format_error_message(err) for err in error_details]
        return jsonify({"message": "Validation error", "details": error_messages}), 400
        
    except IntegrityError as e:
        logger.error(f"Database integrity error: {str(e)}", exc_info=True)
        return jsonify({
            "message": "A database constraint was violated"
        }), 400
        
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}", exc_info=True)
        return jsonify({
            "message": "A database error occurred"
        }), 500
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return jsonify({
            "message": "An unexpected error occurred"
        }), 500
    

@orders_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    current_user_id = get_jwt_identity()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "No JSON data provided"}), 400
        
        order_data = OrderCreate.model_validate(data)
        
        # Start with a new transaction-controlled connection
        with db.engine.begin() as connection:
            # Verify user first - this is now part of the transaction
            query = text("""
            SELECT * FROM auth_verify_user(:user_id)
            """)
            result = connection.execute(query, {"user_id": current_user_id})
            user_row = result.fetchone()
            
            if not user_row:
                # This will automatically roll back the transaction
                return jsonify({"message": "User not found"}), 404
            
            # Create order
            query = text("""
            SELECT * FROM create_order(:user_id, :customer_name)
            """)
            result = connection.execute(
                query, 
                {"user_id": current_user_id, "customer_name": order_data.customer_name}
            )
            order_id = result.scalar()
            
            # Add products
            for product_data in order_data.products:
                query = text("""
                SELECT * FROM create_or_get_product(:name, :price)
                """)
                result = connection.execute(
                    query,
                    {"name": product_data.name, "price": product_data.price}
                )
                product_row = result.fetchone()
            
                unit_price = product_row.price if product_row.price else product_data.price
            
                query = text("""
                SELECT add_product_to_order(:order_id, :product_id, :quantity, :unit_price)
                """)
                connection.execute(
                    query,
                    {
                        "order_id": order_id,
                        "product_id": product_row.id,
                        "quantity": product_data.quantity,
                        "unit_price": unit_price
                    }
                )

            query = text("""
            SELECT * FROM update_order_total(:order_id)
            """)
            result = connection.execute(query, {"order_id": order_id})
            total_price = result.scalar()
            
            # Get order details
            query = text("""
            SELECT * FROM get_order_details(:order_id)
            """)
            result = connection.execute(query, {"order_id": order_id})
            
            order_details = {}
            products = []

            rows = result.fetchall()
            print(rows)
            if rows:
                # Initialize the order details and products
                order_details = {
                    "id": rows[0][0],  # Order ID at index 0
                    "user_id": rows[0][1],  # User ID at index 1
                    "customer_name": rows[0][2],  # Customer name at index 2
                    "total_price": float(rows[0][3]),  # Total price at index 3 (convert Decimal to float)
                    "created_at": rows[0][4],  # Created at at index 4
                    "products": []  # Will be populated below
                }

                # Populate the products list with the first row
                products = [{
                    "id": rows[0][5],  # Product ID at index 5
                    "name": rows[0][6],  # Product name at index 6
                    "quantity": rows[0][7],  # Quantity at index 7
                    "unit_price": float(rows[0][8])  # Unit price at index 8 (convert Decimal to float)
                }]

                # Add any additional products (if any)
                for row in rows[1:]:
                    products.append({
                        "id": row[5],  # Product ID at index 5
                        "name": row[6],  # Product name at index 6
                        "quantity": row[7],  # Quantity at index 7
                        "unit_price": float(row[8])  # Unit price at index 8
                    })

                # Attach the products to order_details
                order_details["products"] = products

                return jsonify({
                    "message": "Order details retrieved successfully",
                    "order": order_details
                }), 200

            else:
                return jsonify({
                    "message": "No order details found"
                }), 404
                
    except ValidationError as e:
        error_details = e.errors()
        error_messages = [format_error_message(err) for err in error_details]
        return jsonify({"message": "Validation error", "details": error_messages}), 400
        
    except IntegrityError as e:
        return jsonify({
            "message": f"Database error: {str(e)}"
        }), 500
        
    except Exception as e:
        return jsonify({
            "message": f"Unexpected error: {str(e)}"
        }), 500