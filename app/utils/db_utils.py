# app/utils/db_utils.py
from app.extensions import db
from sqlalchemy import func
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def optimize_query(query, limit=None):
    """Apply optimizations to a query."""
    if limit:
        query = query.limit(limit)
    return query

def transaction(func):
    """Decorator to manage database transactions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            logger.error(f"Transaction error: {str(e)}", exc_info=True)
            raise e
    return wrapper

def safe_commit():
    """Safely commit transactions with error handling."""
    try:
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Commit error: {str(e)}", exc_info=True)
        return False

class TransactionManager:
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"Transaction error: {str(exc_val)}", exc_info=True)
            db.session.rollback()
            return False
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Commit error: {str(e)}", exc_info=True)
            return False