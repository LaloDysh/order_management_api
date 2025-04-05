from app.extensions import db
from app.models import Product
from sqlalchemy import func


def get_or_create_product(name, price):
    """
    Get an existing product by name or create a new one.
    This helps prevent duplicate products in the database.
    
    Args:
        name (str): Product name
        price (float): Product price
        
    Returns:
        Product: The existing or newly created product
    """
    product = Product.query.filter(func.lower(Product.name) == func.lower(name)).first()
    
    if not product:
        product = Product(name=name, price=price)
        db.session.add(product)
        db.session.flush()  # Flush to get the ID without committing
        
    return product


def optimize_query(query, limit=None):
    """
    Apply performance optimizations to a query.
    
    Args:
        query: SQLAlchemy query object
        limit (int, optional): Maximum number of results
        
    Returns:
        SQLAlchemy query: Optimized query
    """
    # Add query optimization techniques as needed
    if limit:
        query = query.limit(limit)
        
    return query


def transaction(func):
    """
    Decorator for functions that need transaction handling.
    Manages commits and rollbacks automatically.
    
    Usage:
        @transaction
        def my_function(arg1, arg2):
            # Function body
            # No need to commit or handle rollbacks manually
    """
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            raise e
    return wrapper