from datetime import datetime
from flask import request
import re


def validate_email(email):
    """Validate email format"""
    email_regex = r'^\S+@\S+\.\S+$'
    return re.match(email_regex, email) is not None


def parse_date_or_none(date_str):
    """Parse date string in YYYY-MM-DD format"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None


def get_pagination_params():
    """Extract and validate pagination parameters"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Validate parameters
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10
        
    return page, per_page